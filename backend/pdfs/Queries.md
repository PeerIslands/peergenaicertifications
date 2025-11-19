## 1. Generative Adversarial Nets (GANs) – Goodfellow et al., 2014

- What problem were GANs trying to solve in AI?

  - GANs were designed to build generative models that could learn to produce new, realistic-looking data (like images) instead of just classifying existing data.

- How do GANs make fake images look real?

  - They pit two networks against each other: the generator tries to create fake images, while the discriminator tries to spot fakes. Over time, the generator improves until its outputs look convincingly real.

- Why was this paper such a breakthrough in creativity for AI?
  - It was the first framework where machines could generate high-quality, realistic images, opening doors to AI-driven art, design, and data augmentation.

## 2. Going Deeper with Convolutions (GoogLeNet / Inception) – Szegedy et al., 2015

- What was the main idea behind GoogLeNet compared to earlier neural networks?

  - Instead of stacking uniform layers, GoogLeNet introduced Inception modules that process information at multiple scales in parallel, capturing both fine and coarse features.

- How did this model balance accuracy and efficiency?

  - By using 1×1 convolutions as bottlenecks to reduce computation, GoogLeNet achieved state-of-the-art ImageNet results while using fewer parameters than other deep networks of its time.

- What is the Inception module, and why was it a key idea in GoogLeNet?
  - The Inception module is a building block that applies filters of different sizes (1×1, 3×3, 5×5) and pooling in parallel, then merges them. This design let GoogLeNet capture details at multiple scales without making the network too big or slow, thanks to 1×1 convolutions that reduce computation.

## 3. Deep Residual Learning for Image Recognition (ResNet) – He et al., 2015

- What problem do very deep neural networks face, and how does ResNet fix it?

  - As networks got deeper, training accuracy started degrading due to vanishing gradients. ResNet solved this by adding skip (residual) connections that let gradients flow more easily.

- What is the simple trick ResNet introduced to let networks go deeper?

  - It allowed the network to “learn residuals” (changes) instead of mapping inputs to outputs directly, using identity shortcuts. This simple trick enabled training of models with over 100 layers.

- How did ResNet perform compared to previous models on ImageNet?
  - ResNet’s 152-layer model won the ImageNet 2015 competition, achieving a 3.57% top-5 error rate — the best result at the time, and significantly better than earlier deep networks. This success proved that extremely deep networks could be trained effectively when residual connections were used.

## 4. Attention Is All You Need (Transformers) – Vaswani et al., 2017

- What is attention, and why did it replace older sequence models?

  - Attention lets the model focus on the most relevant parts of the input, instead of processing everything step by step like RNNs. This makes it better at capturing long-distance relationships.

- How does this paper explain the benefits of transformers for language tasks?

  - Transformers process tokens in parallel, making training much faster, and they outperform RNNs/LSTMs on tasks like translation because they model long-range dependencies more effectively.

- Why did the authors remove recurrence and convolution from their model?
  - The authors removed recurrence and convolution to make the model faster to train and better at handling long-range dependencies. By relying only on self-attention, the Transformer can process words in parallel and connect distant parts of a sentence more easily than RNNs or CNNs.

## 5. Mercury: Ultra-Fast Diffusion Models – 2024/2025

- What makes Mercury models faster than older AI models?

  - Instead of generating text token-by-token, Mercury uses a coarse-to-fine refinement process that updates many tokens in parallel, achieving massive speedups.

- What breakthrough performance metrics do the Mercury models achieve on GPUs?

  - On standard NVIDIA H100 GPUs, Mercury Coder Mini generates text at 1,109 tokens per second, and Mercury Coder Small achieves 737 tokens per second. These speeds are up to 10 times faster than other leading speed-optimized models—yet maintain similar quality—demonstrating Mercury’s clear edge in both performance and efficiency.

- Why is Mercury considered an important step in scaling AI efficiency?
  - Mercury shows that diffusion-inspired decoding can deliver both speed and quality, making large-scale AI applications more practical and cost-effective.

## 6. SAM 2: Segment Anything in Images and Videos – 2025

- What does SAM 2 let people do with images and videos?

  - It allows users to quickly segment (highlight, cut out, or track) any object in an image or video with simple prompts or clicks.

- How is SAM 2 better than the first version of SAM?

  - SAM 2 extends from static images to videos, adds a streaming memory for object tracking, and runs faster with fewer user inputs.

- How does SAM 2 use past information to improve segmentation in videos?
  - SAM 2 uses a streaming memory mechanism to track objects over time. This memory lets the model remember what an object looked like in earlier frames and use that information to accurately segment and track it in subsequent frames. This is particularly helpful when objects move, disappear, or change appearance—keeping the segmentation consistent and robust.

## 7. Cross Paper Questions

- How did innovations in network design — from Inception (GoogLeNet) to ResNet to Transformers — change the way deep models balance accuracy, depth, and efficiency?

  - Each of these papers introduced a new way to overcome the limits of deep learning: GoogLeNet made deep models more efficient, ResNet made them trainable at extreme depths, and Transformers removed recurrence/convolutions for faster and more scalable sequence modeling. Together, they reshaped the trade-offs between accuracy, depth, and computational cost.

- What are the key differences in how GANs and Mercury create new content?

  - GANs generate content—like realistic images—through a competitive training process: one neural network (the generator) tries to create fake data, while another (the discriminator) evaluates its authenticity. Over time, the generator improves by learning to fool the discriminator, resulting in increasingly realistic outputs.
  - In contrast, Mercury models create content—such as code or text—via a diffusion-inspired, parallel generation approach. Instead of predicting tokens one by one, Mercury refines multiple tokens simultaneously using a coarse-to-fine strategy, which is highly optimized for modern GPU architectures. This enables much faster generation while maintaining high quality.

- How has computer vision advanced from object recognition in GoogLeNet and ResNet, to segmentation in SAM 2?
  - Computer vision has advanced from recognizing and classifying objects in images (GoogLeNet, ResNet setting benchmarks in ImageNet) to understanding and tracking objects at the pixel level across time (SAM 2, segmenting and following objects in videos with memory). This shift moves from “what is in the image” → to “where is it, and how does it change over time,” making vision AI far more practical for real-world applications like AR, robotics, and video editing.
