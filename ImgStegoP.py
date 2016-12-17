#-*- coding:utf-8 -*-
#author:	albertlee
#time:		2016-11-25
import sys
import Image

ending ="[end]" #截断位

def ascii2hex(asc):#return 8字节hex字符串
	_hex = ""
	stp =[0b1, 0b10, 0b100, 0b1000, 0b10000, 0b100000, 0b1000000, 0b10000000]
	for i in xrange(8):
		_hex = _hex + chr((ord(asc) & stp[i]) / stp[i])
	return _hex

def hex2ascii(_hex):#return 1字节字符
	asc = 0
	stp =[0b1, 0b10, 0b100, 0b1000, 0b10000, 0b100000, 0b1000000, 0b10000000]
	for i in xrange(8):
		asc = asc + ord(_hex[i]) * stp[i]
	asc = chr(asc)
	return asc

def Encode(imgfile, payload):#return filename:imgfile-en.imgtype
	try:#打开文件
		f = open(payload,"rb")
	except IOError:
		print "[-] No such file or dictory"
		sys.exit(0)
	text = f.read()
	text = text+ending #文末加截断位
	tlen = len(text)
	f.close()
	print "[*] Loaded payload:%s..." %payload
	print "[+] Payload size: %d Bytes" %tlen
	try:#打开图片
		img = Image.open(imgfile)
	except IOError:
		print "[-] Img open error"
		sys.exit(0)
	img2 = img.copy()
	print "[*] Loaded img:%s..." %imgfile
	width,height = img2.size#宽度，长度
	pix = img2.load()
	try:#像素颜色位深度（如RGB为3）
		pixl = len(pix[0,0])
	except TypeError:#整型值无法取len()，则值为1 
		pixl = 1
	print "[+] BitDepth:%d ,Width:%d ,Height:%d" %(pixl,width,height)
	print "[+] MAX payload size: %d Bytes" %(width*height*pixl/8)
	if width*height*pixl < tlen*8:#可隐写大小判断
		print "[-] payload is larger than img,try another"
		sys.exit(0)
	print "[*] Start encoding..."
	hexs = ""
	for i in xrange(tlen):
		hx = ascii2hex(text[i])#1字节字符转换为8字节hex串
		hexs = hexs+hx
	hlen = len(hexs)

	while hlen%pixl != 0:#以像素颜色位深度倍数补位
		hexs = hexs+'\x00'
		hlen += 1
	#遍历文本
	if pixl == 1:
		for j in xrange(hlen):
			y = j%height#定位像素位置
			x = j/height
			if hexs[j] == '\x00':#设置LSB
				pix[x,y] = pix[x,y]&0b11111110
			else:
				pix[x,y] = pix[x,y]|0b1
	else:#pixl > 1
		for j in xrange(hlen/pixl):
			y = j%height#定位像素位置
			x = j/height
			tmp = list(pix[x,y])
			for k in xrange(pixl):
				if hexs[j*pixl+k] == '\x00':#设置LSB
					tmp[k] = tmp[k]&0b11111110
				else:
					tmp[k] = tmp[k]|0b1
			pix[x,y] = tuple(tmp)
	#保存文件
	savefile = imgfile.split('.')[0]+"-en."+imgfile.split('.')[-1]
	img2.save(savefile)
	img2.show()
	print "[*] Successfully encoded:%s!" %savefile
	pass

def Decode(imgfile):#return filename:imgfile-de-imgtype
	try:
		img = Image.open(imgfile)
	except IOError:
		print "[-] No such file or dictory"
		sys.exit(0)
	img2 = img.copy()
	print "[*] Loaded img:%s..." %imgfile
	width,height = img2.size
	pix = img2.load()
	try:
		pixl = len(pix[0,0])#像素颜色位深度
	except TypeError:
		pixl = 1
	hexs = ""
	print "[*] Start decoding..."
	#遍历像素
	if pixl == 1:
		for x in xrange(width):
			for y in xrange(height):
				if pix[x,y]&0b1 == 1:
					hexs = hexs+'\x01'
				else:
					hexs = hexs+"\x00"
	else:#pixl > 1
		for x in xrange(width):
			for y in xrange(height):
				for i in xrange(pixl):
					if pix[x,y][i]&0b1 == 1:
						hexs = hexs+'\x01'
					else:
						hexs = hexs+"\x00"
	hlen = len(hexs)
	while hlen%8 != 0:
		hexs = hexs[:-1]#去除补位
		hlen -= 1		
	text = ""
	for j in xrange(hlen/8):
		hx = hexs[j*8:j*8+8]#8字节hex串还原1字节字符
		char = hex2ascii(hx)
		text = text+char
	text = text.split(ending)[0]#去除截断位
	print "[+] Recovered file size: %d Bytes" %len(text)
	#保存文件
	savefile = imgfile.split('.')[0]+"-de-"+imgfile.split('.')[-1]
	f = open(savefile,"wb")
	f.write(text)
	f.close()
	print "[*] Successfully encoded:%s!" %savefile


if __name__ == '__main__':
	Encode("02-gray2.png","input3.txt")
	#Decode("02-gray2-en.png")
	

