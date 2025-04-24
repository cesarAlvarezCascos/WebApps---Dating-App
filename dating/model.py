import datetime
from typing import List, Optional

from sqlalchemy import String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON
from flask import current_app
import flask_login
from datetime import date
import enum 
import pathlib

from . import db

class ProposalStatus(enum.Enum):
    proposed = 1
    accepted = 2
    rejected = 3
    ignored = 4
    reschedule = 5

# Enum for Gender
class Gender(enum.Enum):
    male = "Male"
    female = "Female"
    non_binary = "Non_Binary"
    other = "Other"


# Liking and Blocking Associations
class LikingAssociation(db.Model):
    liker_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    liked_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)

class BlockingAssociation(db.Model):
    blocker_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    blocked_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)

# User Model
class User(flask_login.UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(128), unique=True)
    username: Mapped[str] = mapped_column(String(64))
    password: Mapped[str] = mapped_column(String(256))
           
    gender: Mapped["Gender"] = mapped_column(Enum(Gender), nullable=True)   # Enum(Gender) tells SQLAlchemy the domain of the column gender
    year_of_birth: Mapped[int] = mapped_column(nullable=True)
    
    @property
    def age(self): # Compute user.age. It is not a column in the database, just an attribute dinamically created
        current_year = date.today().year
        return current_year - self.year_of_birth

    profile: Mapped["Profile"] = relationship(back_populates="user", uselist=False)

    #posts: Mapped[List["Post"]] = relationship(back_populates="user")

    matching_preferences: Mapped["MatchingPreferences"] = relationship(
        back_populates="user", uselist=False
    )

    liking: Mapped[List["User"]] = relationship(
        secondary=LikingAssociation.__table__,
        primaryjoin=LikingAssociation.liker_id == id,
        secondaryjoin=LikingAssociation.liked_id == id,
        back_populates="likers",
    )
    likers: Mapped[List["User"]] = relationship(
        secondary=LikingAssociation.__table__,
        primaryjoin=LikingAssociation.liked_id == id,
        secondaryjoin=LikingAssociation.liker_id == id,
        back_populates="liking",
    )
    
    blocking: Mapped[List["User"]] = relationship(
        secondary=BlockingAssociation.__table__,
        primaryjoin=BlockingAssociation.blocker_id == id,
        secondaryjoin=BlockingAssociation.blocked_id == id,
        back_populates="blockers",
    )
    blockers: Mapped[List["User"]] = relationship(
        secondary=BlockingAssociation.__table__,
        primaryjoin=BlockingAssociation.blocked_id == id,
        secondaryjoin=BlockingAssociation.blocker_id == id,
        back_populates="blocking",
    )
    sent_proposals: Mapped[List["DateProposal"]] = relationship(
        foreign_keys="DateProposal.proposer_id", 
        back_populates="proposer"
    )
    received_proposals: Mapped[List["DateProposal"]] = relationship(
        foreign_keys="DateProposal.recipient_id", 
        back_populates="recipient"
    )




# Profile Model
class Profile(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True)
    user: Mapped["User"] = relationship(back_populates="profile", single_parent=True)

    name: Mapped[str] = mapped_column(String(64))
    lastname: Mapped[str] = mapped_column(String(64))
    bio: Mapped[Optional[str]] = mapped_column(String(700), nullable=True)

    # One-to-Many Relationship with Photos 
    photos: Mapped[List["Photo"]] = relationship( back_populates="profile", cascade="all, delete-orphan" )


    # Creo que sobra el optional, pq optional es en el form html, pero luego en la base de datos el user tiene que tener una foto si o si

class Photo(db.Model):
    __tablename__ = "photo"
    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profile.id"))
    profile: Mapped["Profile"] = relationship(back_populates="photos")

    file_extension: Mapped[str] = mapped_column(String(8))  # File extension (e.g., "jpg", "png")
    is_profile_photo: Mapped[bool] = mapped_column(default=False)  # True for main profile photo

    @property
    def path(self):
        return photo_filename(self)


def photo_filename(photo):
   
    path = (
        pathlib.Path(current_app.root_path)
        / "static"
        / "img"
        / f"photo-{photo.id}.{photo.file_extension}"
    )
    return path


# Matching Preferences Model
class MatchingPreferences(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True)
    # interested_in_genders: Mapped[List[Gender]] = mapped_column(String(128))  # CSV of genders
    interested_in_genders: Mapped[List["Gender"]] = mapped_column(JSON)  

    min_age_diff: Mapped[int] = mapped_column(default = 0)  
    max_age_diff: Mapped[int] = mapped_column(default = 0)  

    user: Mapped["User"] = relationship(back_populates="matching_preferences")


# Date Proposal Modely l
class DateProposal(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True)) # Date for which the proposal is made
    status: Mapped["ProposalStatus"] = mapped_column(Enum(ProposalStatus))
    proposer_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    proposer: Mapped["User"] = relationship(
        foreign_keys=[proposer_id], back_populates="sent_proposals"
    )
    recipient_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    recipient: Mapped["User"] = relationship(
        foreign_keys=[recipient_id], back_populates="received_proposals"
    )
    proposal_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    response_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    responded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    restaurant_association: Mapped[Optional["DateInRestaurant"]] = relationship(
        back_populates="date_proposal", uselist=False
    )

class Restaurant(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    location: Mapped[str] = mapped_column(String(256))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    
    # Relationships
    availabilities: Mapped[List["Availability"]] = relationship(back_populates="restaurant")
    dates: Mapped[List["DateInRestaurant"]] = relationship(back_populates="restaurant")

class Availability(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurant.id"))
    date: Mapped[datetime.date] = mapped_column(DateTime(timezone=False))
    slots: Mapped[int] = mapped_column(default=0)

    # Relationships
    restaurant: Mapped["Restaurant"] = relationship(back_populates="availabilities")

class DateInRestaurant(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    date_proposal_id: Mapped[int] = mapped_column(ForeignKey("date_proposal.id"))
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurant.id"))
    
    # Relationships
    date_proposal: Mapped["DateProposal"] = relationship(back_populates="restaurant_association")
    restaurant: Mapped["Restaurant"] = relationship(back_populates="dates")
