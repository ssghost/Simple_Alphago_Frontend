import gradio as gr
from tqdm import tqdm
from dcgan import DCGAN
from PIL import Image

self.dcgan = DCGAN()


class Interface:
    def __init__(self):
        self.dcgan = DCGAN()
        self.dsname = gr.inputs.Dropdown(["cifar10", "imagenet_v2", "mnist"])
        self.pbar = gr.outputs.HTML(label = "Training progress:")
        self.image_in = gr.inputs.Image(shape=(224, 224), source="webcam")
        self.image_out = gr.outputs.Image(shape=(224, 224))

    def train_gan(self):
        with tqdm(total=100) as self.pbar: 
            self.dcgan.load_data(self.dsname)
            self.dcgan.make_generator()
            self.dcgan.make_discriminator()
            self.dcgan.generator_loss()
            self.dcgan.discriminator_loss()
            self.dcgan.train()
        return self.pbar

    def launch_train(self):
        gr.Interface(fn=self.train_gan, inputs=self.dsname, outputs=self.pbar, interpretation="default").launch()


    def test_gan(self):
        self.image_in = self.image_in.reshape(1, 28, 28, 1).astype('float32')
        self.image_in = (self.image_in - 127.5) / 127.5
        self.dcgan.save_results(self.dcgan.generator, 50, self.image_in)
        self.image_out = Image.open("./image_at_epoch_0050.png") 
        return self.image_out

    def launch_test(self):
        gr.Interface(fn=self.test_gan, inputs=self.image_in, outputs=self.image_out, interpretation="default").launch()

async def main():
    interface = Interface()
    await interface.train_gan()
    await interface.launch_train()
    await interface.test_gan()
    await interface.launch_test()
