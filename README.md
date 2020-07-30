Invictus Microservice Engineering Task
======================================

Summary
-------
The subfolder Development/V01 contains the images to run. v01.sh will
build and spawn the requisite containers and take you up to the nameko 
shell where you can run the test commands. v01_cleanup.sh will
clean the generated networks, containers and images. You will need to
run them from the V01 folder.

Exploratory, Networking and test_messenger folders were experiments 
performed to link together the various aspects of the architecture.

Purpose
-------
The purpose of this repository is to fulfil the specification outlined
in the Invictus Assessment PDF. The requirements are
- A function that squares each odd number in a given list of integers.
- A function that accepts a list of strings, and returns a dictionary of the strings - the key being
the original string, and the value being a compressed version of that string Huffman.
- A function that decodes a given string previously encoded.

Technologies Used
-----------------
The technologies used in this task are Docker, Python 3.7, Nameko, dahuffman
and RabbitMQ.

**Docker**

Docker allows for containerized deployments. Pros of the technology are
that it is more lightweight than virtual machines, allows all dependencies
to be packaged with the software and guarantees that a docker image will
run on any given host. Cons are that containers do not operate at native
speeds and it takes some skill to reduce the size of a container

**Python 3.7**

A recent stable version of the language that serves as a base for the
control logic

**Nameko**

A microservices framework for Python. Pros are that it allows the developer
to focus on the application logic. It is an implementation for the 
Remote Procedure Call (RPC) specification. A con is that binary data transfer 
with it takes special care. The config.yaml file does not register the names
of docker containers for ip lookup even though utilities like ping and
dig do. The ip address of the RabbitMQ server is looked up when the
nameko container is spawned, and config.yaml dynamically written.

**dahuffman**

dahuffman is a Python module that provides the HuffmanCodec class for
Huffman encoding and decoding. A pro is that it is very simple to use and
produce the results, a con is that saving the data is a bit tedious. There
currently is no string saving option with the save() class method, only
outputs to file. There is also no native API to convert to a format 
that can be sent over the network. The _EOL symbol also requires special
care.

**RabbitMQ**

RabbitMQ implements the AMQP messaging protocol that Nameko needs to
operate. It allows communication of remote procedure calls to the 
microservices framework.

Design Decisions
----------------

The task required quite a few design decisions namely:

- What encoding to use for binary data
- The design of the microservice
- Choice of library for Huffman coding
- Method of storing codec for reuse

Base64 encoding was chosen as the mode of transportation over the network.
This is implemented in the Python Standard Library through the base64
module. A drawback is that file size increases by 33% over the binary version. 
The pickle module was used to serialize the code table for
the Huffman codec to deal with the custom _EOF marker used in the
dahuffman module, and the result base64 encoded for network transfer.

The design of the microservice was inspired by chapter 5 of the Python
Programming Blueprints textbook. The premise is to separate the API
of the microservice from the implementation by using the DependencyProvider
class that is provided with Nameko.

The choice of library for Huffman coding came down to two choices on
PyPI, namely huffman and dahuffman. huffman has had very little activity
over the last two years which may mean that it has been discontinued.
dahuffman was recently updated in the last few months. I chose the latter
package as it seems to have more active development.

The method for storing the codec was to extract the code table from
the dahuffman.HuffmanCodec instance that had been trained on the data.
This was then encoded as in the first paragraph of this section. The
base64 encoded code table was sent along with the resulting Python
dictionary under the "_codec" key. The user must supply this in order
to decode a given encoded string.

Possible Optimizations
----------------------
- There exists a RabbitMQ C client
- Consider the following dockerfiles
    
    
    FROM alpine:3.7
    RUN apk update && apk add --update alpine-sdk
    RUN mkdir /app
    WORKDIR /app
    COPY . /app
    RUN mkdir bin
    RUN gcc -Wall hello.c -o /bin/hello
    CMD /app/bin/hello

and

    FROM alpine:3.7 AS build
    RUN apk update && \
        apk add --update alpine-sdk
    RUN mkdir /app
    WORKDIR /app
    COPY . /app
    RUN mkdir bin
    RUN gcc hello.c -o bin/hello
    
    FROM alpine:3.7
    COPY --from=build /app/bin/hello /app/hello
    CMD /app/hello

Observe the following output

    hello_world_small latest  82274ea4d403  9 seconds ago   4.22MB
    hello_world       latest  cbec3f0583cb  19 seconds ago  178MB

We can see a reduction in size of about 42 times. Smaller image
sizes result in faster startup times and less resource usage. This
seems to be only possible with compiled languages. Python will still
require the toolchain since the interpreter does compile modules to
bytecode now and then.

- For data transfer between Python and C, the ctypes or struct modules
come in handy. This assessment was helpful in showing binary data transfer
over the network and the procedures needed to handle it. For talking
with C, we would only need the RabbitMQ C client, and to use struct.pack()
from the struct module with base64 encoding. Thus remote procedure
calls can be forwarded to other languages from Python. 

Task Times
----------
The times taken for the subtasks are as follows

**General Learning**

1) Docker Engine Installation: 19
2) Nameko, RabbitMQ, Python requirements: 33
3) First microservice: 13
4) Nameko unit testing, redis, integration testing, redis dependency provider: 95
5) Adding/Retrieving message, jinja2 dependency provider: 40
6) POST request, Redis Message Expiry, Sorting messages, Browser Polling: 95
7) Recording learning times: 12

**Experimentation**

1) Exploratory docker image (debian_nameko): 145
2) Exploratory docker image continued (rabbitmq_debian): 87
3) Read Nameko Documentation: 17
4) Create base nameko image (nameko_base): 10
5) Read up about container networking: 23
6) Try test_messenger example again: 90
7) Figure out why nameko shell isn't working: 20

**Building Service**

1) Build invictus service (V01): 238 
2) Code cleanup and commenting: 60
3) Docker entrypoint and dynamic configuration file building: 40
4) README: 80

All times are in minutes. Total time: 1117 minutes ~ 18 hours 37 minutes