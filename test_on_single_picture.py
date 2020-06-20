import tensorflow as tf
from configuration import Config
from core.crnn import CRNN
from core.predict import predict_text


def index_to_char(inputs, idx2char_dict, blank_index, merge_repeated=False):
    chars = []
    for item in inputs:
        text = ""
        pre_char = -1
        for current_char in item:
            if merge_repeated:
                if current_char == pre_char:
                    continue
            pre_char = current_char
            if current_char == blank_index:
                continue
            text += idx2char_dict[current_char]
        chars.append(text)
    return chars


def get_final_output_string(output, blank_index):
    decoded_text = tf.cast(x=output, dtype=tf.int32)
    decoded_text = decoded_text.numpy()
    decoded_text = index_to_char(inputs=decoded_text, idx2char_dict=Config.get_idx2char(), blank_index=blank_index)
    return decoded_text[0]


if __name__ == '__main__':
    # GPU settings
    gpus = tf.config.list_physical_devices("GPU")
    if gpus:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)

    num_classes = len(Config.get_idx2char())
    blank_index = num_classes - 1

    # read image
    image_raw = tf.io.read_file(Config.test_picture_path)
    image_tensor = tf.io.decode_image(contents=image_raw, channels=Config.IAMGE_CHANNELS, dtype=tf.dtypes.float32)
    image_tensor = tf.image.resize(image_tensor, [Config.IMAGE_HEIGHT, Config.IMAGE_WIDTH])
    image_tensor = tf.expand_dims(input=image_tensor, axis=0)

    # load model
    crnn_model = CRNN(num_classes)
    crnn_model.load_weights(filepath=Config.save_model_dir+"saved_model")

    pred = crnn_model(image_tensor, training=False)
    predicted_string = get_final_output_string(predict_text(pred, blank_index), blank_index)
    print(predicted_string)