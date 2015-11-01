from time import time
import threading
import socket
import wolframalpha
client = wolframalpha.Client("2VR45H-HK43G27ALG")




class coupon:
	def __init__(self, title, description, image, initialPrice, value, maxtime, promotionEndTime, counter = 10):
		self.title = title
		self.description = description
		self.image = image
		self.value = value
		self.initialPrice = initialPrice
		self.maxtime = maxtime
		self.promotionEndTime = promotionEndTime
		self.time = time()
		self.counter = counter
		self.n = None
	def changeCoupon(self, title, description, image, initialPrice, value, maxtime, promotionEndTime, counter = 10):
		self.title = title
		self.description = description
		self.image = image
		self.value = value
		self.initialPrice = initialPrice
		self.maxtime = maxtime
		self.promotionEndTime = promotionEndTime
		self.time = time()
		self.counter = counter
	def swapCoupon(self, c):
		self.title = c.title
		self.description = c.description
		self.image = c.image
		self.value = c.value
		self.initialPrice = c.initialPrice
		self.maxtime = c.maxtime
		self.promotionEndTime = c.promotionEndTime
		self.time = time()
		self.counter = c.counter
		self.n = c.next()
	def getTitle(self):
		return self.title
	def getImage(self):
		return self.image
	def setTime(self, t):
		self.time = t
	def resetTime(self):
		if time() < self.promotionEndTime:
			self.time = time()
			return True
		else:
			value = 0
			return False
	def getValue(self):
		x = self.initialPrice - (self.initialPrice * (1 - self.value))
		return self.initialPrice - x * (min(time() - self.time, self.maxtime) ** 2 / self.maxtime ** 2)
	def __ascii__(self):
		return b'{title:"%s", description:"%s", image:"%s", initialPrice:"%d", currentValue:"%f", maxtime:"%d"}' % (self.title, self.description, 
			self.image, self.initialPrice, self.getValue(), self.maxtime)
	def __final__(self):
		res = client.query('QR Code ' + '{product:"%s", discount:"%f"}' % (self.title, 1 - (self.getValue() / self.initialPrice)))
		img = res.pods[1].node._children[0]._children[1].attrib['src']
		return b'{src: "%s", product:"%s", discount:"%f"}' % (img, self.title, 1 - (self.getValue() / self.initialPrice))
	def setNext(self, n):
		self.n = n
	def next(self):
		return self.n

class serverWorker:
	def __init__(self, clientInfo, coupon):
		self.connSocket = clientInfo[0]
		self.clientAddr = clientInfo[1]
		self.coupon = coupon
	def run(self):
		print("Worker running")
		threading.Thread(target=self.work).start()
	def work(self):
		print (self.clientAddr, "has connected.")
		try:
			while True:
				data = self.connSocket.recv(1024)
				print self.clientAddr, "sends:", data
				if data == "":
					break
				elif data == "I want that coupon.":
					
					self.connSocket.sendall(self.coupon.__final__())
					self.coupon.resetTime()
				elif data == "Next coupon please.":
					if self.coupon.next() != None:
						self.coupon.swapCoupon(self.coupon.next())
						self.connSocket.sendall("New Coupon!" + self.coupon.__ascii__())
						print("New Coupon!" + self.coupon.__ascii__())
					else:
						self.connSocket.sendall("No new coupon.")
				else:
					self.connSocket.sendall(self.coupon.__ascii__())
		except socket.error, (code, message):
			print "error processing client", self.clientAddr
		finally:
			print "work is done"
			if self.connSocket:
				self.connSocket.close()
				#this returns only the final coupon price, in reality, it should also give back the coupon or something



class server:
	def __init__(self, coupon, port, maxClients = 5):
		self.coupon = coupon
		self.port = port
		self.maxClients = maxClients
	def run(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
		s.bind(('',self.port))
		s.listen(self.maxClients)
		while True:
			clientInfo = s.accept()
			serverWorker(clientInfo, self.coupon).run()

curve = lambda x, y: x * ((float))
c = coupon(title = "Blendtec Blenders", description = "The most amazing blenders in the world.", image = "http://pics.com", initialPrice = 2000, value = 0.20, maxtime = 60, promotionEndTime = time() + (60 * 60))
c1 = coupon(title = "S-works Tarmac", description = "Carbon that doesn't compromise stiffness for weight, getting the bast of both worlds.", image = "", initialPrice = 10000, value = 0.35, maxtime = 60 * 60, promotionEndTime = time() + 60 * 60 * 2)
c.setNext(c1)

s = server(coupon = c, port = 5000, maxclients = 5)
s.run()


