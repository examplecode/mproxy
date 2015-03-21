#!/usr/bin/python
#-*- coding:utf-8 -*-
 
import socket, logging
import select, errno
import os
import sys
import traceback
import gzip
from StringIO import StringIO
import Queue
import threading
import time
import thread
import cgi
from cgi import parse_qs
import json
import imp
from os.path import join, getsize
import re
import ssl


remote_addr = "23.89.181.214"
remote_port = 8001
local_port = 8003
ENC = 0
DEC = 1

def read_line(client_fd):
	line = ''
	read_len = 0
	while True:
		try:
			data = client_fd.recv(1)
			#print 'read data:%s' % data 
			if not data:
				if data == "":
					break
				else:
					raise Exception("close after process")
			else:
				line += data
				read_len += len(data)
				if data == '\n':
					break
		except socket.error, msg:
			if msg.errno == errno.EAGAIN:
				print msg
				break
			else:
				break
		except Exception, e:
			print e
			break

	return line

def send(remote_fd, datas):
	#print 'begin send, len:%d, content:%s' % (len(datas), datas)
	try:
		send_len = remote_fd.send(datas)
		return send_len
	except socket.error, msg:
		print 'error msg:%s' % msg
		return 0

def recv(remote_fd):
	datas = ''
	while True:
		try:
			data = remote_fd.recv(102400)
			if not data:
				if datas == "":
					break
				else:
					raise Exception("close after process")
			else:
				datas += data
				read_len += len(data)
		except socket.error, msg:
			if msg.errno == errno.EAGAIN:
				process_status = "process"
				break
			else:
				break
		except Exception, e:
			process_status = "close_after_process"
			break
	return datas

def encode(data):
	new_data = bytearray(data)
	data = bytearray(data)
	try:
		for i in range(len(data)):
			if data[i] < 255:
				new_data[i] = data[i] + 1
				#new_data += unichr(ord(c) + 1)
			elif data[i] == 255:
				new_data[i] = 0
			else:
				raise "data encode not right(%d)" % data[i]
	except Exception as e:
		print "encode error(%s)" % e

	return new_data

def decode(data):
	new_data = bytearray(data)
	data = bytearray(data)
	try:
		for i in range(len(data)):
			if data[i] > 0:
				new_data[i] = data[i] - 1
				#new_data += unichr(ord(c) - 1)
			elif data[i] == 0:
				new_data[i] = 255
			else:
				raise "data decode not right(%d)" % data[i]
	except Exception as e:
		print "decode error(%s)" % e
		
	return new_data

def process_socket(client_fd, server_fd, mod):
	BUF_SIZE = 1024
	while True:
		try:
			data = client_fd.recv(BUF_SIZE)
			if not data:
				break
			new_data = ''
			if mod == ENC:
				#print "before encode(%s)" % data
				new_data = encode(data)
			elif mod == DEC:
				new_data = decode(data)
				#print "after decode(%s)" % new_data
			send_len = server_fd.send(new_data)
		except socket.error, msg:
			if msg.errno == errno.EAGAIN:
				continue
		except Exception as e:
			print "error process_socket(%s)" % e
			break
			
def connect(host, port):
	try:
		nextfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
		nextfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		nextfd.settimeout(5)
		try:
			nextfd.connect((host, int(port)))
		except Exception, e:
			print "########%s,%s connect fail" % (host,port)
		nextfd.setblocking(0)
		next_fileno = nextfd.fileno()
		#print "pid:%s, connect %s:%s fd:%s" % (os.getpid(), host, port, next_fileno)
		return nextfd
	except socket.error, msg:
		print msg
		return None

def handler_client(client_fd, addr):

	remote_fd = connect(remote_addr, remote_port)
	if remote_fd is None:
		print 'connect %s:%d error' %(remote_addr, remote_port)
		sys.exit(0)
	
	if os.fork() == 0:
		process_socket(client_fd, remote_fd, ENC)
		sys.exit(0)
	if os.fork() == 0:
		process_socket(remote_fd, client_fd, DEC)
		sys.exit(0)
	
	remote_fd.close()
	client_fd.close()
	#print "ok get back"
	sys.exit(0)

def run_server(listen_fd):
	while True:
		client_fd, addr = listen_fd.accept()
		print 'accepted'
		new_pid = os.fork()
		if new_pid == 0:
			handler_client(client_fd, addr)
			
if __name__ == "__main__":
	
	if len(sys.argv) != 2:
		print "Usage: %s port" % sys.argv[0]
		sys.exit(-1)

	try:
		listen_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
	except socket.error, msg:
		print("create socket failed")
	
	local_port = int(sys.argv[1])
	try:
		listen_fd.bind(('192.168.1.103', local_port))
	except socket.error, msg:
		print("bind failed")
	try:
		listen_fd.listen(5)
	except socket.error, msg:
		print(msg)

	run_server(listen_fd)

