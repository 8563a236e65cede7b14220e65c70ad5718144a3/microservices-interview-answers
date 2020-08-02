/*
    Test rpc client implementation
*/

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <amqp.h>
#include <amqp_tcp_socket.h>

#include <assert.h>

#include "utils.h"

int main(int argc, char** argv){
    char hostname[] = "172.18.0.2";
    int port = 5672, status;
    char exchange[] = "amq.direct";
    char routingkey[] = "test_c";

    char* messagebody = argv[1];

    amqp_socket_t* socket = NULL;
    amqp_connection_state_t conn;
    amqp_bytes_t reply_to_queue;

    amqp_rpc_reply_t amqp_err_check;

    // Create a connection context
    conn = amqp_new_connection();

    // Create a TCP socket for the context
    socket = amqp_tcp_socket_new(conn);
    if(!socket){
        die("creating TCP socket");
    }

    // Open the socket with connection details
    status = amqp_socket_open(socket, hostname, port);
    if(status){
        die("Opening TCP socket");
    }

    // Attempt a login into RabbitMQ server
    // amqp_login(
    //    amqp_connection_state_t state,
    //    char const *vhost, int channel_max,
    //    int frame_max, int heartbeat,
    //    amqp_sasl_method_enum sasl_method, ...)

    amqp_err_check = amqp_login(
        conn, "/", 0,
        131072, 0,
        AMQP_SASL_METHOD_PLAIN,
        "guest", "guest"
    );

    // Check for errors and exit if found
    die_on_amqp_error(amqp_err_check, "Logging in");

    // Open a channel
    //amqp_channel_open(amqp_connection_state_t state,
    //                  amqp_channel_t channel)
    // state - connection state
    // channel - channel to do RPC on
    amqp_channel_open(conn, 1);

    // Check for errors
    die_on_amqp_error(amqp_get_rpc_reply(conn), "Opening Channel");
    {
        // Create a private reply_to queue
        amqp_queue_declare_ok_t* r;

        r = amqp_queue_declare(
            conn, 1, amqp_empty_bytes, 0, 0, 0, 1, amqp_empty_table
        );

        // Error check
        amqp_err_check = amqp_get_rpc_reply(conn);
        die_on_amqp_error(amqp_err_check, "Declaring queue");

        // Map reply_to_queue
        reply_to_queue = amqp_bytes_malloc_dup(r->queue);
        if(reply_to_queue.bytes == NULL){
            printf("Out of memory while copying queue name");
            return 1;
        }
    }

    // Send the message

    {
        /*
            Set the Properties

            Flags for RPC:
                AMQP_BASIC_CONTENT_TYPE_FLAG
                AMQP_BASIC_DELIVERY_MODE_FLAG
                AMQP_BASIC_REPLY_TO_FLAG        indicate reply is wanted
                AMQP_BASIC_CORRELATION_ID_FLAG  correlation id for
                                                return
        */
        amqp_basic_properties_t props;
        props._flags = AMQP_BASIC_CONTENT_TYPE_FLAG |
                        AMQP_BASIC_DELIVERY_MODE_FLAG |
                        AMQP_BASIC_REPLY_TO_FLAG |
                        AMQP_BASIC_CORRELATION_ID_FLAG;
        props.content_type = amqp_cstring_bytes("text/plain");
        props.delivery_mode = 2;
        props.reply_to = amqp_bytes_malloc_dup(reply_to_queue);
        if(props.reply_to.bytes == NULL){
            printf("Out of memory while copying queue name");
            return 1;
        }
        props.correlation_id = amqp_cstring_bytes("1");

        /*
            Publish
        */
        die_on_error(
            amqp_basic_publish(
                conn, 1, amqp_cstring_bytes(exchange),
                amqp_cstring_bytes(routingkey), 0, 0,
                &props, amqp_cstring_bytes(messagebody)
            ),
            "Publishing"
        );
        amqp_bytes_free(props.reply_to);
    }

    /*
        Wait for an answer
    */
    {
        amqp_basic_consume(conn, 1, reply_to_queue, amqp_empty_bytes,
            0, 1, 0, amqp_empty_table);
        amqp_err_check = amqp_get_rpc_reply(conn);
        die_on_amqp_error(amqp_err_check, "Consuming");
        amqp_bytes_free(reply_to_queue);

        /*
            Read response frames
        */
        {
            amqp_frame_t frame;
            int result;

            amqp_basic_deliver_t* d;
            amqp_basic_properties_t* p;
            size_t body_target;
            size_t body_received;

            for(;;){
                amqp_maybe_release_buffers(conn);
                result = amqp_simple_wait_frame(conn, &frame);
                printf("Result: %d\n", result);
                if(result < 0){
                    break;
                }

                printf("Frame type: %u channel: %u",
                    frame.frame_type,
                    frame.channel
                );
                if(frame.frame_type != AMQP_FRAME_METHOD){
                    continue;
                }

                printf("Method: %s\n",
                    amqp_method_name(frame.payload.method.id)
                );
                if(frame.payload.method.id != AMQP_BASIC_DELIVER_METHOD){
                    continue;
                }

                d = (amqp_basic_deliver_t* )frame.payload.method.decoded;
                printf("Delivery: %u exchange %.*s routingkey: %.*s\n",
                    (unsigned)d->delivery_tag, (int)d->exchange.len,
                    (char* )d->exchange.bytes, (int)d->routing_key.len,
                    (char* )d->routing_key.bytes
                );

                result = amqp_simple_wait_frame(conn, &frame);
                if(result < 0){
                    break;
                }

                if(frame.frame_type != AMQP_FRAME_HEADER){
                    printf("Expected header!");
                    abort();
                }

                p = (amqp_basic_properties_t* )frame.payload.properties.decoded;
                if(p->_flags & AMQP_BASIC_CONTENT_TYPE_FLAG){
                    printf("Content-type: %.*s\n",
                        (int)p->content_type.len,
                        (char* )p->content_type.bytes
                    );
                }
                printf("----\n");

                body_target = (size_t)frame.payload.properties.body_size;
                body_received = 0;

                while(body_received < body_target){
                    result = amqp_simple_wait_frame(conn, &frame);
                    if(result < 0){
                        break;
                    }

                    if(frame.frame_type != AMQP_FRAME_BODY){
                        printf("Expected body!");
                        abort();
                    }

                    body_received += frame.payload.body_fragment.len;
                    assert(body_received <= body_target);

                    amqp_dump(frame.payload.body_fragment.bytes,
                        frame.payload.body_fragment.len
                    );
                }

                if(body_received != body_target){
                    break;
                }

                break;

            }
        }
    }

    die_on_amqp_error(
        amqp_channel_close(conn, 1, AMQP_REPLY_SUCCESS),
        "Closing channel"
    );

    die_on_amqp_error(
        amqp_connection_close(conn, AMQP_REPLY_SUCCESS),
        "Closing channel"
    );

    die_on_error(amqp_destroy_connection(conn), "Ending Connection");
}