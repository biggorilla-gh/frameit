
from frameit import SRL
from frameit.api.api_wrapper import create_app
from frameit.api.answerer import Answerer

srl = SRL()
srl.loadFrame("hotel_facility_v003.json")

answerer = Answerer(srl)

app = create_app(answerer)

# this is a hack to fix the current issue
srl.parse('Do you have a pool?')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5559)


