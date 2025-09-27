from motor.motor_asyncio import (
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
    AsyncIOMotorGridFSBucket,
)


class Collections:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.users: AsyncIOMotorCollection = db["users"]
        self.workspaces: AsyncIOMotorCollection = db["workspaces"]
        self.resume_parsed: AsyncIOMotorCollection = db["resume_parsed"]
        self.job_descriptions: AsyncIOMotorCollection = db["job_descriptions"]

        self.resume_files: AsyncIOMotorGridFSBucket = AsyncIOMotorGridFSBucket(
            db, bucket_name="resume_files"
        )
        # Underlying files collection for queries
        self.resume_files_collection: AsyncIOMotorCollection = db["resume_files.files"]
