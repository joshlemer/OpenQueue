from models import *

#Users
user1 = User(user_id=123,email='joshlemer@gmail.com',isAdmin=True)
user2 = User(user_id=456,email='tashivani@gmail.com',isAdmin=False)
user3 = User(user_id=789,email='joshu@gmail.com',isAdmin=False)
user4 = User(user_id=321,email='fakemail@gmail.com',isAdmin=False)

users = [user1, user2, user3, user4]

for user in users:
	user.set_password('password')
	user.save()

users = [user.reload() for user in users]

#Rooms
room1 = Room(name='Room 1')
room2 = Room(name='Room 2')
room3 = Room(name='Room 3')
room4 = Room(name='Room 4')

rooms = [room1, room2, room3, room4]

for room in rooms:
	room.save()

rooms = [room.reload() for room in rooms]

#Resources
res1 = Resource(name='Beta A')
res2 = Resource(name='Beta B')
res3 = Resource(name='Beta C')
res4 = Resource(name='Beta A')
res5 = Resource(name='Beta A')
res6 = Resource(name='Beta A')
res7 = Resource(name='Beta B')
res8 = Resource(name='Beta C')
res9 = Resource(name='Beta B')
res10 = Resource(name='Beta C')
res11 = Resource(name='Beta B')
res12 = Resource(name='Beta C')

resources = [res1, res2, res3, res4, res5, res6, res7, res8, res9, res10, res11, res12 ]

for resource in resources:
	resource.save()

resources = [resource.reload() for resource in resources]

#Queues
r1q1 = Queue(name='Betas q1',resources=[resources[0],resources[1]],room=rooms[0])
r1q2 = Queue(name='Betas q2',resources=[resources[2]],room=rooms[0])

r2q1 = Queue(name='Betas q1',resources=[resources[3],resources[4]],room=rooms[1])
r2q2 = Queue(name='Betas q2',resources=[resources[5]],room=rooms[1])

r3q1 = Queue(name='Betas q1',resources=[resources[6],resources[7]],room=rooms[0])
r3q2 = Queue(name='Betas q2',resources=[resources[8]],room=rooms[2])

queues = [r1q1, r1q2, r2q1, r2q2, r3q1, r3q2]

for queue in queues:
	queue.save()

queues = [queue.reload() for queue in queues]

rooms[0].queues.append(queues[0])
rooms[0].queues.append(queues[1])
rooms[1].queues.append(queues[2])
rooms[1].queues.append(queues[3])
rooms[2].queues.append(queues[4])
rooms[2].queues.append(queues[5])

rooms = [room.save() for room in rooms]
rooms = [room.reload() for room in rooms]


# #Queue Elements

# qe1 = QueueElement(user=user1,accepts=[res1,res2])
# qe2 = QueueElement(user=user2,accepts=[res2])
# qe3 = QueueElement(user=user3,accepts=[res3])
# qe4 = QueueElement(user=user4,accepts=[res3])
