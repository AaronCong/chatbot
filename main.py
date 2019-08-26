from deeppavlov import build_model, configs

model = build_model('custombot_config.json')

utterance = ""
while utterance != 'exit':
    print(">> " + model([utterance])[0])
    utterance = input(':: ')
