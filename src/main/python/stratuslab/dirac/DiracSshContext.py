"""
This function has been copied from the Nova11.py file.  It uses an SSH connection
to the machine to copy files to the virtual machine instance and to run the
DIRAC contextualization script.

Note: This method has hardcoded values for the SSH keys.  The same keys must be
used for the StratusLab Libcloud configuration.
"""

import os
import paramiko
import time

try:
    from DIRAC import gLogger, S_OK, S_ERROR
except:
    from stratuslab.dirac.DiracMock import gLogger, S_OK, S_ERROR


class DiracSshContext (object):

    @staticmethod
    def sshContextualise(uniqueId,
                         publicIP,
                         cloudDriver,
                         cvmfs_http_proxy,
                         vmStopPolicy,
                         contextMethod,
                         vmCertPath,
                         vmKeyPath,
                         vmContextualizeScriptPath,
                         vmRunJobAgentURL,
                         vmRunVmMonitorAgentURL,
                         vmRunVmUpdaterAgentURL,
                         vmRunLogAgentURL,
                         vmCvmfsContextURL,
                         vmDiracContextURL,
                         siteName,
                         cpuTime):
        # the contextualization using ssh needs the VM to be ACTIVE, so VirtualMachineContextualization
        # check status and launch contextualize_VMInstance

        # 1) copy the necesary files

        # prepare paramiko sftp client
        try:
            privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
            mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
            sshusername = 'root'
            transport = paramiko.Transport(( publicIP, 22 ))
            transport.connect(username=sshusername, pkey=mykey)
            sftp = paramiko.SFTPClient.from_transport(transport)
        except Exception, errmsg:
            return S_ERROR("Can't open sftp conection to %s: %s" % ( publicIP, errmsg ))

        # scp VM cert/key
        putCertPath = "/root/vmservicecert.pem"
        putKeyPath = "/root/vmservicekey.pem"
        try:
            sftp.put(vmCertPath, putCertPath)
            sftp.put(vmKeyPath, putKeyPath)
            # while the ssh.exec_command is asyncronous request I need to put on the VM the contextualize-script to ensure the file existence before exec
            sftp.put(vmContextualizeScriptPath, '/root/contextualize-script.bash')
        except Exception, errmsg:
            return S_ERROR(errmsg)
        finally:
            sftp.close()
            transport.close()

            # giving time sleep asyncronous sftp
        time.sleep(5)


        #2)  prepare paramiko ssh client
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(publicIP, username=sshusername, port=22, pkey=mykey)
        except Exception, errmsg:
            return S_ERROR("Can't open ssh conection to %s: %s" % ( publicIP, errmsg ))

        #3) Run the DIRAC contextualization orchestator script:

        try:
            remotecmd = "/bin/bash /root/contextualize-script.bash \'%s\' \'%s\' \'%s\' \'%s\' \'%s\' \'%s\' \'%s\' \'%s\' \'%s\' \'%s\' \'%s\' \'%s\' \'%s\' \'%s\'"
            remotecmd = remotecmd % ( uniqueId, putCertPath, putKeyPath, vmRunJobAgentURL,
                                      vmRunVmMonitorAgentURL, vmRunVmUpdaterAgentURL, vmRunLogAgentURL,
                                      vmCvmfsContextURL, vmDiracContextURL, cvmfs_http_proxy, siteName, cloudDriver,
                                      cpuTime, vmStopPolicy )
            print "remotecmd"
            print remotecmd
            _stdin, _stdout, _stderr = ssh.exec_command(remotecmd)
        except Exception, errmsg:
            return S_ERROR("Can't run remote ssh to %s: %s" % ( publicIP, errmsg ))

        return S_OK()
