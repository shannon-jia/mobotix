import socket
from threading import Thread
from time import sleep

def dealWithClient(newSocket,destAddr):
    while True:
        recvData = newSocket.recv(1024)
        if len(recvData)>0:
            print('recv[%s]:%s'%(str(destAddr),recvData))
        else:
            print('[%s]客户端已经关闭'%str(destAddr))
        break
    newSocket.close()

def main():
    serSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    serSocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    localAddr = ('',9009)
    serSocket.bind(localAddr)
    serSocket.listen(5)

    try:
        while True:
            print('主进程===等待新的客户端进来')
            newSocket,DestAddr = serSocket.accept()
            print('主进程接下来创建一个新的线程来执行与客户端的交互')
            client = Thread(target=dealWithClient,args=(newSocket,DestAddr))
            client.start()
            #因为线程中共享这个套接字，如果关闭了导致这个套接字不可用
            newSocket.close()
    finally:serSocket.close()

if __name__ == '__main__':
    main()
