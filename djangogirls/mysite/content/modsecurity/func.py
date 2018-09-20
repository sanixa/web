import os
import getpass

def nginx():
    try: 
        os.popen("ps -C nginx | grep -v CMD | awk '{print $1}'").readlines()[0]
    except IndexError:
        return "no run"
    else:
        return "run"

def nginx_modsecurity():
    TEMP_FILE_PATH = "./tempf"
    try: 
        os.popen("ps -C nginx | grep -v CMD | awk '{print $1}'").readlines()[0]
    except IndexError:
        return "error"
    s = os.popen("ps -C nginx | grep -v CMD | awk '{print $1}'").readlines()[0]
    s = "ls -l /proc/" + s[:s.find("/n")] + "/exe > " + TEMP_FILE_PATH   #process detail
    os.system(s)
    f = open(TEMP_FILE_PATH , 'r')
    s = f.readline()
    f.close()
    s = s[s.find('>')+2:-1] + " -V 2> " + TEMP_FILE_PATH
    os.popen(s)
    f = open(TEMP_FILE_PATH , 'r')
    for line in f:
        if line.find('modsecurity') != -1:
            return "yes"
    return "no"

def mod_custom_rule(cmd):
    os.system("touch /usr/local/nginx/conf/custom.conf")
    try:
        f = open("/usr/local/nginx/conf/modsec_includes.conf" , 'r+')
    except IOError:
        return "error"
    boolean = 0
    for line in f:
        if line == "include custom.conf\n":
            boolean = 1
    if boolean == 0:
        f.write("include custom.conf\n")
    f.close()
    
    f = open("/usr/local/nginx/conf/custom.conf", 'a')
    f.write(cmd + "\n")
    return "success"

def stop_nginx():
    os.system("sudo systemctl stop nginx.service")

def restart_nginx():
    os.system("sudo systemctl restart nginx.service")

#def main():
    #stop_nginx()
#if __name__ == "__main__":
    #main()
