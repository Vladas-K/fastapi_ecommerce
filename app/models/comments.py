from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, Float  # New
from sqlalchemy.orm import relationship
# New

from app.backend.db import Base


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    comment = Column(String)
    comment_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    grade = Column(Integer)
    is_active = Column(Boolean)

    product = relationship('Product', back_populates='comments')
    user = relationship('User', back_populates='comments')