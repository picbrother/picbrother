
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Boolean, Table, ForeignKey
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

	photos = relationship('Photo', secondary=photo_users, backref=__tablename__)

	def __repr__(self):
		return "<User('%s','%s', '%s')>" % (self.fb_id, self.first_name, self.last_name)


class Album(Base):
	__tablename__ = 'T_ALBUM'

	id = Column(Integer, primary_key=True)
	fb_id = Column(BigInteger, unique=True)
	name = Column(String(255), nullable=False)

	photos = relationship('Photo', order_by="Photo.id", backref='T_ALBUM')



class Photo(Base):
	__tablename__ = 'T_PHOTO'

	id = Column(Integer, primary_key=True)
	fb_id = Column(BigInteger, unique=True)
	url = Column(String(512), unique=True, nullable=False)
	album_id = Column(Integer, ForeignKey(Album.__tablename__+'.id'), nullable=False)

	users = relationship('User', secondary=photo_users, backref=__tablename__)
	album = relationship('Album', backref=backref(__tablename__, order_by=id))

	def __repr__(self):
		return "<Photo('%s')>" % (self.url,)


class MysqlAPI:
	def __init__(self, host, user, pswd, db, *, verbose=False):
		s = 'mysql+oursql://{user}:{pswd}@{host}/{db}'.format(
			host=host,
			user=user,
			pswd=pswd,
			db=db
		)
		self._engine = create_engine(s, echo=verbose)
		Base.metadata.create_all(self._engine)
		self._session = sessionmaker(bind=self._engine)()

	def get_fb_user(self, fb_id):
		return self._get_fb_object(User, fb_id)
	
	def get_fb_photo(self, fb_id):
		return self._get_fb_object(Photo, fb_id)

	def get_fb_album(self, fb_id):
		return self._get_fb_object(Album, fb_id)

	def _get_fb_object(self, cls, fb_id):
		try:
			return self._session.query(cls).filter_by(fb_id=fb_id).one()
		except MultipleResultsFound as ex:
			print(ex)
		except NoResultFound:
			pass
	
	def add_object(self, o):
		error = ""
		self._session.add(o)
		try:
			self._session.commit()
			return o
		except IntegrityError as ex:
			error = str(ex)
			self._session.rollback()
		return error
	
	def update(self):
		self._session.commit()

if __name__ == '__main__':
	api = MysqlAPI('localhost', 'root', 'root', 'picbrother', verbose=True)
	album = Album(fb_id="1234", name="coucou")
	api.add_object(album)
	user = User(
		fb_id=1161312122,
		first_name="thomas",
		last_name="recouvreux",
	)
	
	api.add_object(user)
	user2 = User(
		first_name="bid", last_name="on"
	)
	api.add_object(user2)
	user = api.get_fb_user(fb_id='1161312122')
	print(user)
	print(user.photos)
	photo = Photo(
		fb_id = "1234",
		url = "http://bidon.com/photo.img",
		album = album,
	)
	photo.users.extend([user, user2])
	photo = api.add_object(photo)
	print(photo)
