from deeppavlov import build_model, configs

model = build_model('custombot_config.json')
# model = build_model(configs.go_bot.gobot_dstc2)
utterance = ""
while utterance != 'exit':
    print(">> " + model([utterance])[0])
    utterance = input(':: ')
