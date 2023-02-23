import json

from util.route import route
from util.log import logger
import openai
import tornado.web
from bot import bot_factory
import requests
from util.config import conf

openai.api_key = conf().get('open_ai_api_key')
dd_token = conf().get("dingtalk_accessToken")

# Set up the model and prompt
model_engine = "text-davinci-003"

retry_times = 5

@route("/")
class ChatgptHandler(tornado.web.RequestHandler):

    def get(self):
        return self.write_json({"ret": 200})

    def post(self):

        request_data = self.request.body;
        data = json.loads(request_data)
        prompt = data['text']['content']

        # for i in range(retry_times):
        #     try:
        #         completion = openai.Completion.create(
        #             model="text-davinci-003",  # 对话模型的名称
        #             prompt=prompt,
        #             temperature=0.9,  # 值在[0,1]之间，越大表示回复越具有不确定性
        #             max_tokens=1200,  # 回复最大的字符数
        #             top_p=1,
        #             frequency_penalty=0.0,  # [-2,2]之间，该值越大则更倾向于产生不同的内容
        #             presence_penalty=0.0,  # [-2,2]之间，该值越大则更倾向于产生不同的内容
        #             stop=["#"]
        #         )
        #         response = completion.choices[0]["text"].strip().rstrip("<|im_end|>")
        #         logger.info(f"[OPEN_AI] reply= {response}")
        #         break
        #     except:
        #         logger.info(f"failed, retry")
        #         continue
        logger.info(f"request_date = {prompt}")
        response = bot_factory.create_bot("openAI").reply(prompt, dict())

        logger.info(f"parse response: {response}")
        self.notify_dingding(response)
        return self.write_json({"ret": 200})

    def write_json(self, struct):
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(tornado.escape.json_encode(struct))

    def notify_dingding(self, answer):
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": "chatgpt: ",
                "text": answer
            },

            "at": {
                "atMobiles": [
                    ""
                ],
                "isAtAll": False
            }
        }


        notify_url = f"https://oapi.dingtalk.com/robot/send?access_token={dd_token}"
        try:
            r = requests.post(notify_url, json=data)
            reply = r.json()
            logger.info("dingding: " + str(reply))
        except Exception as e:
            logger.error(e)
