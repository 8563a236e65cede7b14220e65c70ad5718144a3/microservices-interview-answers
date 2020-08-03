#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <amqp.h>
#include <amqp_tcp_socket.h>

#include <assert.h>
#include "utils.h"

struct Credentials {
    char* username;
    char* password;
    int erase_on_connect;
};


struct Dict {
    char** keys;
    char** values;
};

struct ConnectionParameters {
    char* host;
    int port;
    char* virtual_host;
    struct Credentials credentials;
    int channel_max;
    int frame_max;
    int heartbeat;
    int connection_attempts;
    int retry_delay;
    int socket_timeout;
    int stack_timeout;
    char* locale;
    int blocked_connection_timeout;
    struct Dict client_properties;
    struct Dict tcp_options;
};

struct Connection {
    amqp_connection_state_t conn;
    amqp_socket_t *socket;
};

struct ConnectionParameters init_connection_parameters(){

    struct ConnectionParameters s;

    s.host = NULL;
    s.port = 5672;
    s.virtual_host = strdup("/");
    s.channel_max = 0;
    s.frame_max = 131072;
    s.heartbeat = 0;
    s.credentials.username = strdup("guest");
    s.credentials.password = strdup("guest");

    return s;

}

void connection_channel(struct Connection connection, int channel){
    amqp_channel_open(connection.conn, channel);
    die_on_amqp_error(amqp_get_rpc_reply(connection.conn), "Opening channel");
}

amqp_bytes_t channel_queue_declare(struct Connection connection,
    char* queue){
    amqp_bytes_t queuename;
    amqp_queue_declare_ok_t *r = amqp_queue_declare(
        connection.conn, 1, amqp_cstring_bytes(queue),
        0, 0, 0, 1, amqp_empty_table);
    die_on_amqp_error(amqp_get_rpc_reply(connection.conn), "Declaring queue");
    queuename = amqp_bytes_malloc_dup(r->queue);
    if (queuename.bytes == NULL) {
      fprintf(stderr, "Out of memory while copying queue name");
      exit(EXIT_FAILURE);
    }

    return queuename;

}

void channel_bind_queue(struct Connection connection, amqp_bytes_t queuename,
        char* exchange, char* bindingkey
    ){
    amqp_queue_bind(connection.conn, 1, queuename, amqp_cstring_bytes(exchange),
                    amqp_cstring_bytes(bindingkey), amqp_empty_table);
    die_on_amqp_error(amqp_get_rpc_reply(connection.conn), "Binding queue");
}

void channel_basic_consume(struct Connection connection, amqp_bytes_t queuename){
  amqp_basic_consume(connection.conn, 1, queuename, amqp_empty_bytes, 0, 1, 0,
                     amqp_empty_table);
  die_on_amqp_error(amqp_get_rpc_reply(connection.conn), "Consuming");
}

void channel_start_consuming(struct Connection connection){
    for (;;) {
      amqp_rpc_reply_t res;
      amqp_envelope_t envelope;

      amqp_maybe_release_buffers(connection.conn);

      res = amqp_consume_message(connection.conn, &envelope, NULL, 0);

      if (AMQP_RESPONSE_NORMAL != res.reply_type) {
        break;
      }

      printf("Delivery %u, exchange %.*s routingkey %.*s\n",
             (unsigned)envelope.delivery_tag, (int)envelope.exchange.len,
             (char *)envelope.exchange.bytes, (int)envelope.routing_key.len,
             (char *)envelope.routing_key.bytes);

      if (envelope.message.properties._flags & AMQP_BASIC_CONTENT_TYPE_FLAG) {
        printf("Content-type: %.*s\n",
               (int)envelope.message.properties.content_type.len,
               (char *)envelope.message.properties.content_type.bytes);
      }
      printf("----\n");

      amqp_dump(envelope.message.body.bytes, envelope.message.body.len);

      amqp_destroy_envelope(&envelope);
    }
}

void cleanup(struct Connection connection, amqp_bytes_t queuename){
    amqp_bytes_free(queuename);

    die_on_amqp_error(amqp_channel_close(connection.conn, 1, AMQP_REPLY_SUCCESS),
                      "Closing channel");
    die_on_amqp_error(amqp_connection_close(connection.conn, AMQP_REPLY_SUCCESS),
                      "Closing connection");
    die_on_error(amqp_destroy_connection(connection.conn), "Ending connection");
}

struct Connection blocking_connection(
    struct ConnectionParameters param
    ){

    int status;
    struct Connection self;

    self.conn = amqp_new_connection();

    self.socket = amqp_tcp_socket_new(self.conn);
    if (!self.socket) {
        die("creating TCP socket");
    }

    status = amqp_socket_open(self.socket, param.host, param.port);
    if (status) {
        die("opening TCP socket");
    }

    die_on_amqp_error(
        amqp_login(
            self.conn,
            param.virtual_host,
            param.channel_max,
            param.frame_max,
            param.heartbeat,
            AMQP_SASL_METHOD_PLAIN,
            param.credentials.username,
            param.credentials.password
            ),
    "Logging in");

    return self;
}

int main(int argc, char** argv){

    char exchange[] = "";
    char bindingkey[] = "";
    struct Connection conn;
    amqp_bytes_t queuename;
    struct ConnectionParameters conn_par =
        init_connection_parameters();

    conn_par.host = strdup("172.18.0.2");
    conn = blocking_connection(conn_par);

    connection_channel(conn, 1);

    queuename = channel_queue_declare(conn, "hello2");
    printf("queuename = %.*s\n", queuename.len, queuename.bytes);

    // Not permitted on default queue
    //channel_bind_queue(conn, queuename, exchange, bindingkey);

    channel_basic_consume(conn, queuename);

    channel_start_consuming(conn);

    cleanup(conn, queuename);

}