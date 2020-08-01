/*
 *  Test server Implementation
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

    // The AMQP connection needs the hostname, port,
    // exchange type (amq.direct, amq.fanout, amq.topic, amq.match)
    // and binding key to create the connection
    char hostname[] = "172.17.0.3";
    int port = 5672, status;
    char exchange[] = "amq.direct";
    char bindingkey[] = "test_c";

    // Declare socket and connection state variables
    amqp_socket_t* socket = NULL;
    amqp_connection_state_t conn;

    // Declare a queue name variable
    amqp_bytes_t queuename;

    // Declare an rpc response variable
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
    //  amqp_connection_state_t state,
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
    die_on_amqp_error(amqp_err_check, "Opening Channel");

    // Declare a queue
    // amqp_queue_declare(
    //     amqp_connection_state_t state, amqp_channel_t channel, amqp_bytes_t queue,
    //     amqp_boolean_t passive, amqp_boolean_t durable, amqp_boolean_t exclusive,
    //     amqp_boolean_t auto_delete, amqp_table_t arguments);
    {
        amqp_queue_declare_ok_t* r;
        r = amqp_queue_declare(
            conn, 1, amqp_empty_bytes, 0, 0, 0, 1, amqp_empty_table
        );

        // Check if queue was created successfully
        amqp_err_check = amqp_get_rpc_reply(conn);
        die_on_amqp_error(amqp_err_check, "Declaring queue");

        // Copy the queue name
        queuename = amqp_bytes_malloc_dup(r->queue);
        if(queuename.bytes == NULL){
            printf("Out of memory while copying queue name");
            return 1;
        }
    }

    // Bind the queue to the exchange name and routing key
    amqp_queue_bind(
        conn, 1, queuename, amqp_cstring_bytes(exchange),
        amqp_cstring_bytes(bindingkey), amqp_empty_table
    );

    // Check for errors
    amqp_err_check = amqp_get_rpc_reply(conn);
    die_on_amqp_error(amqp_err_check, "Binding queue");

    // Consume
    amqp_basic_consume(
        conn, 1, queuename, amqp_empty_bytes, 0, 1, 0,
        amqp_empty_table
    );

    // Check for errors
    amqp_err_check = amqp_get_rpc_reply(conn);
    die_on_amqp_error(amqp_err_check, "Consuming");

    // Main event loop

    /*
        typedef struct amqp_envelope_t_ {
            amqp_channel_t channel;     channel message was delivered on

            amqp_bytes_t consumer_tag;  the consumer tag the message was
                                        delivered to

            uint64_t delivery_tag;      the messages delivery tag

            amqp_boolean_t redelivered; flag indicating whether this message
                                        is being redelivered

            amqp_bytes_t exchange;      exchange this message was published to

            amqp_bytes_t routing_key;   the routing key this message was published
                                        with

            amqp_message_t message;     the message
        } amqp_envelope_t;

        typedef struct amqp_message_t_ {
            amqp_basic_properties_t properties; message properties

            amqp_bytes_t body;                  message body

            amqp_pool_t pool;                   pool used to allocate properties
        } amqp_message_t;


        typedef struct amqp_bytes_t_ {
            size_t len;     length of the buffer in bytes
            void *bytes;    pointer to the beginning of the buffer
        } amqp_bytes_t;
    */
    {
        for(;;){

            amqp_rpc_reply_t res;
            amqp_envelope_t envelope;

            amqp_maybe_release_buffers(conn);

            res = amqp_consume_message(conn, &envelope, NULL, 0);
            if(AMQP_RESPONSE_NORMAL != res.reply_type){
                break;
            }

            printf("%.*s\n",
                (int)envelope.message.body.len,
                (char* )envelope.message.body.bytes
            );

            amqp_destroy_envelope(&envelope);
        }
    }

    amqp_bytes_free(queuename);

    die_on_amqp_error(
        amqp_channel_close(conn, 1, AMQP_REPLY_SUCCESS),
        "Closing channel"
    );

    die_on_amqp_error(
        amqp_connection_close(conn, AMQP_REPLY_SUCCESS),
        "Closing channel"
    );

    die_on_error(amqp_destroy_connection(conn), "Ending Connection");

    return 0;

 }
