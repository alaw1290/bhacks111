from time import time
#import threading, socket
from tornado import web, websocket, ioloop
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
		return b'{"title":"%s", "description":"%s", "image":"%s", "initialPrice":"%d", "currentValue":"%f", "maxtime":"%d"}' % (self.title, self.description, 
			self.image, self.initialPrice, self.getValue(), self.maxtime)
	def __final__(self):
		res = client.query('QR Code ' + '{product:"%s", discount:"%f"}' % (self.title, 1 - (self.getValue() / self.initialPrice)))
		img = res.pods[1].node._children[0]._children[1].attrib['src']
		return b'{"src": "%s", "product":"%s", "discount":"%f"}' % (img, self.title, 1 - (self.getValue() / self.initialPrice))
	def setNext(self, n):
		self.n = n
	def next(self):
		return self.n


'''
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
'''

c = coupon(title = "Blendtec Blenders", description = "The most amazing blenders in the world.", image = "http://osd.archive.neverbehind.com/wp-content/uploads/import/2013-522/Blendtec-Blender.jpg", initialPrice = 2000, value = 0.20, maxtime = 60, promotionEndTime = time() + (60 * 60))
c1 = coupon(title = "S-works Tarmac", description = "Carbon that doesn't compromise stiffness for weight, getting the bast of both worlds.", image = "http://s7d5.scene7.com/is/image/Specialized/145080?$Hero$", initialPrice = 10000, value = 0.35, maxtime = 60 * 60, promotionEndTime = time() + 60 * 60 * 2)
c2 = coupon(title = "Krispy Kreme", description = "So good, you'll suck a dick. - Chris Rock", image = "http://www.newhealthadvisor.com/images/1HT00255/krispy+kreme4.jpg", initialPrice = 12, value = 0.10, maxtime = 60, promotionEndTime = time() + 60 * 60 * 2)
c3 = coupon(title = "Male Grooming Kit", description = "Shout out to Adrian", image = "https://laynecorban.files.wordpress.com/2012/01/misterr-nesbitt-grooming-kit-1.jpg", initialPrice = 500, value = 0.15, maxtime = 60, promotionEndTime = time() + 60 * 60 * 2)
c4 = coupon(title = "Full Body Sleeping Bag", description = "Get Sexiled in Style.", image = "http://i.imgur.com/oJxbxqi.jpg", initialPrice = 85, value = 0.75, maxtime = 60, promotionEndTime = time() + 60 * 60 * 2)

c3.setNect(c4)
c2.setNect(c3)
c1.setNect(c2)
c.setNext(c1)

class WebSocketHandler(websocket.WebSocketHandler):
	def check_origin(self, origin):
		return True
	
	def open(self):
		print "New client connected"
		self.write_message(c.__ascii__())

	def on_message(self, message):
		if message == 'I want that coupon.':
			self.write_message(c.__final__())
			c.resetTime()
		elif message == 'Next coupon please.':
			if c.next != None:
				c.swapCoupon(c.next())
				self.write_message(c.__ascii__())
			else:
				self.write_message('No new message.')
		else:
			self.write_message(c.__ascii__())

	def on_close(self):
		print "Client disconnected"

application = web.Application([
    (r"/", WebSocketHandler),
])
 
if __name__ == "__main__":
    application.listen(5000)
    ioloop.IOLoop.instance().start()


'''
s = server(coupon = c, port = 5000, maxClients = 5)
s.run()
'''

