from app.models.schema.fastapi.db_collections import Collections
from app.models.schema.user.user_update import UserUpdate


async def update_user(user_id: str, update_data: UserUpdate, collections: Collections):
    data_dict = update_data.dict(exclude_unset=True)
    if not data_dict:
        return await collections.users.find_one({"_id": user_id})

    updated_user = await collections.users.find_one_and_update(
        {"_id": user_id}, {"$set": data_dict}, return_document=True
    )

    if not updated_user:
        raise ValueError(f"User with id {user_id} not found")

    return updated_user
