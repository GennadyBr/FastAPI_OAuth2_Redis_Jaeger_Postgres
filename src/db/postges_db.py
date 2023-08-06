from db.abstract import AbstractDB


class PostgresqlDB(AbstractDB):
    async def create(self, new_object):
        """Create new db item"""

    async def read(self, item_id):
        """Read the db item"""

    async def update(self, item_id, new_object):
        """Update db item"""

    async def delete(self, item_id):
        """Delete the db item"""
