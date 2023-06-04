#!/usr/bin/env python3
import os

# Alexander Stepanov (c) 2021

# ----------------------------------------
#   Please set your parameters here
# ----------------------------------------

# Number of nodes
nodes = 2

# GG version (you must place here a desired image name from DockerHub)
base_image = "gridgain/community:8.7.35-openjdk8"

# TcpDiscoveryPort
tcp_discovery_Port = 47500

# ----------------------------------------


print("Starting to generate configuration files for creating node images")

# List of template files
template_files = os.listdir("./templates/")

os.system("sudo docker-compose down")
os.system("find -type d -name 'node*' -exec sudo rm -rf {} \\;")

d_compose_file = open("./docker-compose.yml", "w")
d_compose_file.write("version: \"3\"\nservices:\n")

coordinator_name = ""

for i in range(0, nodes):
    # Generating folder's name (the same as image name)
    image_name = "node{:03d}".format(i)
    if i == 0:
        coordinator_name = image_name
        print("Coordinator: " + coordinator_name)
    image_folder = "./" + image_name
    try:
        os.makedirs(image_folder + "/work")
        os.system("chmod 777 " + image_folder + "/work")
    except OSError:
        print("Creation of the directory %s failed" % image_folder)

    # Copy templates and replace tags into node's folder
    for templ_file in template_files:
        src_file = open("./templates/" + templ_file, "r")
        dst_file = open(image_folder + "/" + templ_file, "w")
        # Replace tags
        template_content = src_file.readlines()
        for src_line in template_content:
            # Search and replace  <<bla-bla>> with real data
            src_line = src_line.replace("<<base_docker_image>>", base_image)
            src_line = src_line.replace("<<consistentId>>", image_name)
            src_line = src_line.replace("<<tcp_discovery_ports_range>>",
                                        str(tcp_discovery_Port) + ".." + str(tcp_discovery_Port + nodes - 1))
            dst_file.write(src_line)
            #
        dst_file.close()
        src_file.close()

    d_compose_file.write("\n" + " " * 2 + image_name + ":\n" +
                         " " * 4 + "image: " + base_image + "\n" +
                         " " * 4 + "volumes:\n" +
                         " " * 6 + "- '" + image_folder + ":/gg'\n" +
                         " " * 4 + "command: /opt/gridgain/bin/ignite.sh /gg/gg_config.xml" + "\n" +
                         #" " * 4 + "command: touch /gg/work/ttt.txt" + "\n" +
                         " " * 4 + "ports:\n" +
                         " " * 6 + "- 11211\n" +
                         " " * 6 + "- 47100\n" +
                         " " * 6 + "- 47500\n" +
                         " " * 6 + "- 49112"
                         )
    if i != 0:
        d_compose_file.write("\n" + " " * 4 + "depends_on:\n" +
                             " " * 6 + "- " + coordinator_name)
    d_compose_file.write("\n")
d_compose_file.close()

os.system("sudo -S docker-compose up")
