#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 1999-2018, Juniper Networks Inc.
#               2016, Damien Garros
#
# All rights reserved.
#
# License: Apache 2.0
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
# * Neither the name of the Juniper Networks nor the
#   names of its contributors may be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY Juniper Networks, Inc. ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Juniper Networks, Inc. BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

from __future__ import absolute_import, division, print_function
import hashlib
from jnpr.junos.utils.scp import SCP

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'supported_by': 'community',
                    'status': ['stableinterface']}

DOCUMENTATION = '''
---
extends_documentation_fragment: 
  - juniper_junos_common.connection_documentation
  - juniper_junos_common.logging_documentation
module: juniper_junos_ping
version_added: "2.0.0" # of Juniper.junos role
author: Juniper Networks - Stacy Smith (@stacywsmith)
short_description: Execute ping from a Junos device
description:
  - Execute the ping command from a Junos device to a specified destination in
    order to test network reachability from the Junos device .
options:
  acceptable_percent_loss:
    description:
        - Maximum percentage of packets that may be lost and still consider the
          task not to have failed.
    required: false
    default: 0
    type: int
    aliases:
      - acceptable_packet_loss
  count:
    description:
      - Number of packets to send.
    required: false
    default: 5
    type: int
  dest:
    description:
      - The IP address, or hostname if DNS is configured on the Junos device,
        used as the destination of the ping.
    required: true
    default: none
    type: str
    aliases:
      - dest_ip
      - dest_host
      - destination
      - destination_ip
      - destination_host
  do_not_fragment:
    description:
      - Set Do Not Fragment bit on ping packets.
    required: false
    default: false
    type: bool
  interface:
    description:
      - The source interface from which the the ping is sent. If not
        specified, the default Junos algorithm for determining the source
        interface is used.
    required: false
    default: none
    type: str
  rapid:
    description:
      - Send ping requests rapidly
    required: false
    default: true
    type: bool
  routing_instance:
    description:
      - Name of the source routing instance from which the ping is
        originated. If not specified, the default routing instance is used.
    required: false
    default: none
    type: str
  size:
    description:
      - The size of the ICMP payload of the ping.
      - Total size of the IP packet is I(size) + the 20 byte IP header +
        the 8 byte ICMP header. Therefore, I(size) of C(1472) generates an IP
        packet of size 1500.
    required: false
    default: none (default size for device)
    type: int
  source:
    description:
      - The IP address, or hostname if DNS is configured on the Junos device,
        used as the source address of the ping. If not specified, the Junos
        default algorithm for determining the source address is used.
    required: false
    default: none
    type: str
    aliases:
      - source_ip
      - source_host
      - src
      - src_ip
      - src_host
  ttl:
    description:
      - Maximum number of IP routers (hops) allowed between source and
        destination.
    required: false
    default: none (default ttl for device)
    type: int
'''

EXAMPLES = '''
---
- name: Examples of juniper_junos_ping
  hosts: junos-all
  connection: local
  gather_facts: no
  roles:
    - Juniper.junos

  tasks:
    - name: Ping 10.0.0.1 with default parameters. Fails if any packets lost.
      juniper_junos_ping:
        dest: "10.0.0.1"

    - name: Ping 10.0.0.1. Allow 50% packet loss. Register response.
      juniper_junos_ping:
        dest: "10.0.0.1"
        acceptable_percent_loss: 50
      register: response
    - name: Print all keys in the response.
      debug:
        var: response

    - name: Ping 10.0.0.1. Send 20 packets. Register response.
      juniper_junos_ping:
        dest: "10.0.0.1"
        count: 20
      register: response
    - name: Print packet sent from the response.
      debug:
        var: response.packets_sent

    - name: Ping 10.0.0.1. Send 10 packets wihtout rapid. Register response.
      juniper_junos_ping:
        dest: "10.0.0.1"
        count: 10
        rapid: false
      register: response
    - name: Print the average round-trip-time from the response.
      debug:
        var: response.rtt_average

    - name: Ping www.juniper.net with ttl 15. Register response.
      juniper_junos_ping:
        dest: "www.juniper.net"
        ttl: 15
      register: response
    - name: Print the packet_loss percentage from the response.
      debug:
        var: response.packet_loss

    - name: Ping 10.0.0.1 with IP packet size of 1500. Register response.
      juniper_junos_ping:
        dest: "10.0.0.1"
        size: 1472
      register: response
    - name: Print the packets_received from the response.
      debug:
        var: response.packets_received

    - name: Ping 10.0.0.1 with do-not-fragment bit set. Register response.
      juniper_junos_ping:
        dest: "10.0.0.1"
        do_not_fragment: true
      register: response
    - name: Print the maximum round-trip-time from the response.
      debug:
        var: response.rtt_maximum

    - name: Ping 10.0.0.1 with source set to 10.0.0.2. Register response.
      juniper_junos_ping:
        dest: "10.0.0.1"
        source: "10.0.0.2"
      register: response
    - name: Print the source from the response.
      debug:
        var: response.source

    - name: Ping 192.168.1.1 from the red routing-instance.
      juniper_junos_ping:
        dest: "192.168.1.1"
        routing_instance: "red"

    - name: Ping the all-hosts multicast address from the ge-0/0/0.0 interface
      juniper_junos_ping:
        dest: "224.0.0.1"
        interface: "ge-0/0/0.0"
'''

RETURN = '''
acceptable_percent_loss:
  description:
    - The acceptable packet loss (as a percentage) for this task as specified
      by the I(acceptable_percent_loss) option.
  returned: when ping successfully executed, even if the
            I(acceptable_percent_loss) was exceeded.
  type: str
changed:
  description:
    - Indicates if the device's state has changed. Since this module
      doesn't change the operational or configuration state of the
      device, the value is always set to C(false).
  returned: when ping successfully executed, even if the
            I(acceptable_percent_loss) was exceeded.
  type: bool
count:
  description:
    - The number of pings sent, as specified by the I(count) option.
  returned: when ping successfully executed, even if the
            I(acceptable_percent_loss) was exceeded.
  type: str
do_not_fragment:
  description:
    - Whether or not the do not fragment bit was set on the pings sent, as
      specified by the I(do_not_fragment) option.
  returned: when ping successfully executed, even if the
            I(acceptable_percent_loss) was exceeded.
  type: bool
failed:
  description:
    - Indicates if the task failed.
  returned: always
  type: bool
host:
  description:
    - The destination IP/host of the pings sent as specified by the I(dest)
      option.
    - Keys I(dest) and I(dest_ip) are also returned for backwards
      compatibility.
  returned: when ping successfully executed, even if the
            I(acceptable_percent_loss) was exceeded.
  type: str
interface:
  description:
    - The source interface of the pings sent as specified by the
      I(interface) option.
  returned: when ping successfully executed and the I(interface) option was
            specified, even if the I(acceptable_percent_loss) was exceeded.
  type: str
msg:
  description:
    - A human-readable message indicating the result.
  returned: always
  type: str
packet_loss:
  description:
    - The percentage of packets lost.
  returned: when ping successfully executed, even if the
            I(acceptable_percent_loss) was exceeded.
  type: str
packets_sent:
  description:
    - The number of packets sent.
  returned: when ping successfully executed, even if the
            I(acceptable_percent_loss) was exceeded.
  type: str
packets_received:
  description:
    - The number of packets received.
  returned: when ping successfully executed, even if the
            I(acceptable_percent_loss) was exceeded.
  type: str
rapid:
  description:
    - Whether or not the pings were sent rapidly, as specified by the
      I(rapid) option.
  returned: when ping successfully executed, even if the
            I(acceptable_percent_loss) was exceeded.
  type: bool
routing_instance:
  description:
    - The routing-instance from which the pings were sent as specified by
      the I(routing_instance) option.
  returned: when ping successfully executed and the I(routing_instance)
            option was specified, even if the I(acceptable_percent_loss) was
            exceeded.
  type: str
rtt_average:
  description:
    - The average round-trip-time, in microseconds, of all ping responses
      received.
  returned: when ping successfully executed, and I(packet_loss) < 100%.
  type: str
rtt_maximum:
  description:
    - The maximum round-trip-time, in microseconds, of all ping responses
      received.
  returned: when ping successfully executed, and I(packet_loss) < 100%.
  type: str
rtt_minimum:
  description:
    - The minimum round-trip-time, in microseconds, of all ping responses
      received.
  returned: when ping successfully executed, and I(packet_loss) < 100%.
  type: str
rtt_stddev:
  description:
    - The standard deviation of round-trip-time, in microseconds, of all ping
      responses received.
  returned: when ping successfully executed, and I(packet_loss) < 100%.
  type: str
size:
  description:
    - The size in bytes of the ICMP payload on the pings sent as specified
      by the I(size) option.
    - Total size of the IP packet is I(size) + the 20 byte IP header + the 8
      byte ICMP header. Therefore, I(size) of 1472 generates an IP packet of
      size 1500.
  returned: when ping successfully executed and the I(size) option was
            specified, even if the I(acceptable_percent_loss) was exceeded.
  type: str
source:
  description:
    - The source IP/host of the pings sent as specified by the I(source)
      option.
    - Key I(source_ip) is also returned for backwards compatibility.
  returned: when ping successfully executed and the I(source) option was
            specified, even if the I(acceptable_percent_loss) was exceeded.
  type: str
timeout:
  description:
    - The number of seconds to wait for a response from the ping RPC.
  returned: when ping successfully executed, even if the
            I(acceptable_percent_loss) was exceeded.
  type: str
ttl:
  description:
    - The time-to-live set on the pings sent as specified by the
      I(ttl) option.
  returned: when ping successfully executed and the I(ttl) option was
            specified, even if the I(acceptable_percent_loss) was exceeded.
  type: str
warnings:
  description:
    - A list of warning strings, if any, produced from the ping.
  returned: when warnings are present
  type: list
'''


def import_juniper_junos_common():
    """Imports the juniper_junos_common module from _module_utils_path.

    Ansible versions < 2.4 do not provide a way to package common code in a
    role. This function solves that problem for juniper_junos_* modules by
    reading the module arguments passed on stdin and interpreting the special
    option _module_utils_path as a path to the the directory where the
    juniper_junos_common module resides. It temporarily inserts this path at
    the head of sys.path, imports the juniper_junos_common module, and removes
    the path from sys.path. It then returns the imported juniper_junos_common
    module object. All juniper_junos_* modules must include this boilerplate
    function in order to import the shared juniper_junos_common module.

    Args:
        None.

    Returns:
        The juniper_junos_common module object.

    Raises:
        ImportError: If the juniper_junos_common object can not be imported
                     from the path specified by the module_utils_path argument.
    """
    from ansible.module_utils.basic import AnsibleModule
    import sys
    
    juniper_junos_common = None
    module = AnsibleModule(
        argument_spec={
            '_module_utils_path': dict(type='path', default=None),
            # Avoids a warning about not specifying no_log for passwd.
            'passwd': dict(no_log=True)
        },
        # Doesn't really work due to Ansible bug. Keeping it here for when
        # Ansible bug is fixed.
        no_log=True,
        check_invalid_arguments=False,
        bypass_checks=True
    )
    import_path = module.params.get('_module_utils_path')
    if import_path is not None:
        sys.path.insert(0, import_path)
        import juniper_junos_common
        del sys.path[0]
    return juniper_junos_common


def _hashfile(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest()


def local_md5(junos_module, package):
    """
    Computes the MD5 checksum value on the local package file.

    :param str package:
      File-path to the package (\*.tgz) file on the local server

    :returns: MD5 checksum (str)
    :raises IOError: when **package** file does not exist
    """
    try:
        checksum=_hashfile(open(package, 'rb'), hashlib.md5())
    except Exception as err:
        junos_module.logger.error("unable to get the hash due to:{0}".format(err))
        if (("No such file" in format(err)) and (junos_module.params['type']=="get")):
            checksum="no_file"
        else:
            raise err
        return checksum

    junos_module.logger.info("local hash calculated")
    return checksum


def remote_md5(junos_module, remote_file):
    try:
        rpc_reply=junos_module.dev.rpc.get_checksum_information(path=remote_file)
        checksum=rpc_reply.findtext('.//checksum').strip() 
    except Exception as err:
       junos_module.logger.error("unable to get rpc due to:{0}".format(err.message))
       if (("No such file or directory" in err.message) and (junos_module.params['type']=="put")):
           checksum="no_file" 
       else:
           raise err
       return checksum
    junos_module.logger.info("rpc reponse recvd")
    return checksum


def main():
    # Import juniper_junos_common
    juniper_junos_common = import_juniper_junos_common()

    # The argument spec for the module.
    argument_spec = dict(
        local_dir=dict(type='str',
                  required=True,
                  default=None),
        remote_dir=dict(type='str',
                  required=True,
                  default=None),
        file=dict(type='str',
                  required=True,
                  default=None), 
        type=dict(type='str',
                  choices=['put', 'get'], 
                  required=True,
                  default=None)
    )

    # Create the module instance.
    junos_module = juniper_junos_common.JuniperJunosModule(
        argument_spec=argument_spec,
        supports_check_mode=False ## TODO Need to add support for Check
    )

    # Set initial results values. Assume failure until we know it's success.
    results = {'msg': '', 'changed': False, 'failed': False}

    # We're going to be using params a lot
    params = junos_module.params

    junos_module.logger.info("Starting the file transfer: {0}".format(params['file']))

    remote_path=params['remote_dir']
    
    local_file=params['local_dir']+"/"+params['file']
    remote_file=params['remote_dir']+"/"+params['file']
    if (params['type'] == "put"):
        junos_module.logger.info('computing local MD5 checksum on: %s' % local_file)
        local_checksum = local_md5(junos_module, local_file)
        junos_module.logger.info('Local checksum: %s' % local_checksum) 
        remote_checksum = remote_md5(junos_module, remote_file)
        if ((remote_checksum == "no_file") or (remote_checksum != local_checksum)):
            status="File not present, need to transfert" 
            junos_module.logger.info(status)

            with SCP(junos_module.dev) as scp1:
                scp1.put(local_file,remote_path)

            # validate checksum:
            junos_module.logger.info('computing remote MD5 checksum on: %s' % remote_file)
            remote_checksum = remote_md5(junos_module, remote_file)
            junos_module.logger.info('Remote checksum: %s' % remote_checksum)
            if remote_checksum != local_checksum:
                status="Transfer failed (different MD5 between local and remote) {} | {}".format( 
                        local_checksum,
                        remote_checksum
                    )
                junos_module.logger.error(status)
                junos_module.fail_json(msg=status)
                return False
            else:
                junos_module.logger.info("checksum check passed.")
                status="File pushed OK"
                results['changed'] = True
        else: 
            status="File already present, skipping the scp" 
            junos_module.logger.info(status)

    if (params['type'] == "get"): 
        junos_module.logger.info('computing remote MD5 checksum on: %s' % remote_file)
        remote_checksum = remote_md5(junos_module, remote_file)
        junos_module.logger.info('Remote checksum: %s' % remote_checksum)
        local_checksum = local_md5(junos_module, local_file)
        if ((local_checksum == "no_file") or (remote_checksum != local_checksum)):

            with SCP(junos_module.dev) as scp1:
                scp1.get(remote_file,local_file)

            # validate checksum:
            junos_module.logger.info('Computing local MD5 checksum on: %s' % local_file)
            local_checksum = local_md5(junos_module, local_file)
            junos_module.logger.info('Local checksum: %s' % local_checksum)

            if remote_checksum != local_checksum:
                junos_module.logger.error("Checksum check failed.")
                status="Transfer failed (different MD5 between local and remote) {} | {}".format( 
                        local_checksum,
                        remote_checksum
                    )
                junos_module.fail_json(msg=status)
                return False
            else:
                junos_module.logger.info("Checksum check passed.")

                status="File retrieved OK"
                results['changed'] = True

        else:
            status="File already present, skipping the scp"
            junos_module.logger.info(status)

    results['msg'] = status

    # Return results.
    junos_module.exit_json(**results)


if __name__ == '__main__':
    main()
