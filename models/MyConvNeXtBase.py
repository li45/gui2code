import tensorflow.keras as keras
from tensorflow.keras import layers


class MyConvNeXtBase(keras.Model):
    def __init__(self, num_classes, img_size=224):
        super().__init__()
        self._input_shape = (img_size, img_size, 3)
        self.rescaling = layers.Rescaling(1. / 255, input_shape=self._input_shape)
        self.base_model = keras.applications.convnext.ConvNeXtBase(
            include_top=False,
            weights='imagenet',
            input_shape=self._input_shape
        )
        # 冻结原网络的权重，不参与新数据集的训练。
        self.base_model.trainable=False
        self.globalAveragePooling2D = keras.layers.GlobalAveragePooling2D()
        self.dense = keras.layers.Dense(num_classes)
        self.input_layer = keras.layers.Input(self._input_shape)
        self.out = self.call(self.input_layer)

    def call(self, input_tensor, training=False):
        x = self.rescaling(input_tensor)
        x = self.base_model(x)
        x = self.globalAveragePooling2D(x)
        x = self.dense(x)
        return x


