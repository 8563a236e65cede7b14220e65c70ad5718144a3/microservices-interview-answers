/*
 * Test client implementation
 */

 #include <stdint.h>
 #include <stdio.h>
 #include <stdlib.h>
 #include <string.h>

 #include <amqp.h>
 #include <amqp_tcp_socket.h>

 #include "utils.h"

 int main(int argc, char** argv){

    char hostname[] = "172.17.0.3";
    int port = 5672, status;
    char exchange[] = "amq.direct";
    char routingkey[] = "test_c";

    char* messagebody = argv[1];

    amqp_socket_t* socket = NULL;
    amqp_connection_state_t conn;

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
        amqp_basic_properties_t props;

        props._flags = AMQP_BASIC_CONTENT_TYPE_FLAG | AMQP_BASIC_DELIVERY_MODE_FLAG;
        props.content_type = amqp_cstring_bytes("text/plain");
        props.delivery_mode = 2;

        die_on_error(
            amqp_basic_publish(
                conn, 1, amqp_cstring_bytes(exchange),
                amqp_cstring_bytes(routingkey), 0, 0,
                &props, amqp_cstring_bytes(messagebody)
            ),
            "Publishing"
        );
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