import datetime

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
"""Flask have an ecosystem where package gets installed to this ext(external area)
module. and inside of that we get the package.
Read About UserMixin - 'http://flask-login.readthedocs.org/en/latest/#your-user-class'
"""

from peewee import *

DATABASE = SqliteDatabase('new.db')

class User(UserMixin, Model):
	"""Parent class can be more than one"""
	__searchable__ = ['name']
	username = CharField(unique = True)
	email = CharField(unique = True)
	password = CharField(max_length = 100)
	joined_at = DateTimeField(default = datetime.datetime.now)
	is_admin = BooleanField(default = False)

	class Meta:
		database = DATABASE
		order_by = ('-joined_at',)

	def get_posts(self):
		return Post.select().where(Post.user == self)

	def get_stream(self):
		return Post.select().where(
			(Post.user << self.following()),
			(Post.user == self)
			)

	def following(self):
		"""The users we are following"""
		return(
			User.select().join(
				Relationship, on=Relationship.to_user
				).where(
					Relationship.from_user == self
				)
			)

	def followers(self):
		"""Users Following the current user"""
		return(
			User.select().join(
				Relationship, on=Relationship.from_user
				).where(
					Relationship.to_user == self
				)
			)

	@classmethod
	def create_user(cls, username, email, password, admin=False):
		"""cls here is being user. so cls.create is kind of user.create"""
		try:
			with DATABASE.transaction():
				cls.create(
					username = username,
					email = email,
					password = generate_password_hash(password),
					is_admin = admin
					)
		except IntegrityError:
			raise ValueError("User already exists")


class Post(Model):
	timestamp = DateTimeField(default = datetime.datetime.now)
	user = ForeignKeyField(
		User,
		related_name = 'posts'
	)
	# likes = IntegerField(default=0)
	# liked = BooleanField(default=False)
	content = TextField()

	def likes(self):
		"""Users Following the current user"""
		return(
			User.select().join(
				LikedPost, on=LikedPost.from_user
				).where(
					LikedPost.to_post == self
				)
			)
	class Meta:
		database = DATABASE
		order_by = ('-timestamp',)

class Relationship(Model):
	from_user = ForeignKeyField(User, related_name='relationships')
	to_user = ForeignKeyField(User, related_name='related_to')

	class Meta:
		database = DATABASE
		indexes = (
				(('from_user','to_user'), True),
			)

class LikedPost(Model):
	from_user = ForeignKeyField(User, related_name='relationships')
	to_post = ForeignKeyField(Post, related_name='related_to')

	class Meta:
		database = DATABASE
		indexes = (
				(('from_user','to_post'), True),
			)
def initialize():
	DATABASE.connect()
	DATABASE.create_tables([User, Post, Relationship, LikedPost], safe = True)
	DATABASE.close()