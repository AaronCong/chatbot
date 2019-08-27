from deeppavlov import build_model, configs

model = build_model('custombot_config.json')
# model = build_model(configs.seq2seq_go_bot.bot_kvret, download=True)
# model = build_model(configs.go_bot.gobot_dstc2)
utterance = ""
while utterance != 'exit':
    print(">> " + model([utterance])[0])
    utterance = input(':: ')


# dialog_id = '2b77c100-0fec-426a-a483-04ac03763776' # or any other dialog id from train dataset
# while utterance != 'exit':
#     print(">> " + model([utterance], [dialog_id])[0])
#     utterance = input(':: ')