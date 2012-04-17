
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Table, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.exc import IntegrityError

Base = declarative_base()


# table de relation many to many
photo_users = Table('J_PHOTO_USER', Base.metadata,
	Column('photo_id', Integer, ForeignKey('T_PHOTO.id')),
	Column('user_id', Integer, ForeignKey('T_USER.id'))
)

class User(Base):
	__tablename__ = 'T_USER'

	id = Column(Integer, primary_key=True)
	fb_id = Column(BigInteger, unique=True)
	first_name = Column(String(100), nullable=False)
	last_name = Column(String(100), nullable=False)

	photos = relationship('Photo', secondary=photo_users, backref='T_USER')

	def __repr__(self):
		return "<User('%s','%s', '%s')>" % (self.fb_id, self.first_name, self.last_name)


class Photo(Base):
	__tablename__ = 'T_PHOTO'

	id = Column(Integer, primary_key=True)
	fb_id = Column(BigInteger, unique=True)
	url = Column(String(512), unique=True, nullable=False)

	users = relationship('User', secondary=photo_users, backref='T_PHOTO')

	def __repr__(self):
		return "<Photo('%s')>" % (self.url,)


class MysqlAPI:
	def __init__(self, host, user, pswd, db, *, verbose=False):
		s = 'mysql://{user}:{pswd}@{host}/{db}'.format(
			host=host,
			user=user,
			pswd=pswd,
			db=db
		)
		self._engine = create_engine(s, echo=verbose)
		Base.metadata.create_all(self._engine)
		self._session = sessionmaker(bind=self._engine)()

	def get_fb_user(self, fb_id):
		try:
			return self._session.query(User).filter_by(fb_id=fb_id).one()
		except MultipleResultsFound as ex:
			print(ex)
		except NoResultFound:
			pass

	def add_user(self, user):
		error = ""
		user.first_name = user.first_name.lower()
		user.last_name = user.last_name.lower()
		self._session.add(user)
		try:
			self._session.commit()
		except IntegrityError as ex:
			error = str(ex)
			self._session.rollback()
		return error
	
	def get_fb_photo(self, fb_id):
		try:
			return self._session.query(Photo).filter_by(fb_id=fb_id).one()
		except MultipleResultsFound as ex:
			print(ex)
		except NoResultFound:
			pass
			
	def add_photo(self, photo):
		error = ""
		self._session.add(photo)
		try:
			self._session.commit()
			return photo
		except IntegrityError as ex:
			error = str(ex)
			self._session.rollback()
		return error

	def update(self):
		self._session.commit()

if __name__ == '__main__':
	api = MysqlAPI('localhost', 'root', 'root', 'picbrother', verbose=True)
	user = User(
		fb_id=1161312122,
		first_name="thomas",
		last_name="recouvreux",
	)
	api.add_user(user)
	user2 = User(
		first_name="bid", last_name="on"
	)
	api.add_user(user2)
	user = api.get_fb_user(fb_id='1161312122')
	print(user)
	print(user.photos)
	photo = Photo(
		fb_id = "1234",
		url = "http://bidon.com/photo.img"
	)
	photo.users.extend([user, user2])
	photo = api.add_photo(photo)
	print(photo)
