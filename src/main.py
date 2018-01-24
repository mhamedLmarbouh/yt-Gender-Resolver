from src.services import scrapper
from src.datastore.factory import DatabaseFactory


db=DatabaseFactory().build().get_database_service()
res=db.find_by_videoId("-UAvLhaF-Eg",projection={"_id":0,"authorChannelUrl":1})
data = scrapper.get_googleplus_data(res[:50])

print(data)