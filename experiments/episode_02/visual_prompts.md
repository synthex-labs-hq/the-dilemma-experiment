# AI Visual & Video Generation Prompts: Episode 2

A unified production guide combining **Visual Aesthetics + Motion Direction** in single, ready-to-use prompts.

---

## 📐 How Aspect Ratios Are Separated

| Format | Aspect Ratio | Target Output | Composition Strategy |
| :--- | :---: | :--- | :--- |
| **Widescreen Landscape** | **`16:9`** | YouTube Long Video (~2:45), Article Cover Art | Wide horizon, panoramic depth, subjects arrayed horizontally, cinematic breathing room. |
| **Vertical Portrait** | **`9:16`** | YouTube Shorts, TikTok, Instagram Reels | Towering vertical lines, foreground-to-background stacking, center-weighted action with top/bottom safe margins for UI. |

---

## 🎬 How to Use These Combined Prompts

You can use each prompt in **two ways**:
1. **All-in-One Text-to-Video (T2V)** (Hailuo / Minimax, Kling AI, Luma Dream Machine, Runway Gen-3):  
   Paste the prompt directly. It contains both the visual scene description and the integrated camera motion direction.
2. **Image-to-Video (I2V)** (Google Gemini / ChatGPT / Midjourney $\rightarrow$ Video Animator):  
   - First, paste the prompt into Gemini / ChatGPT / Midjourney with the specified aspect ratio (`--ar 16:9` or `--ar 9:16`) to generate the high-res still image.
   - Then, upload that image into Hailuo / Kling / PixVerse and paste the provided **Motion Cue** in the motion box.

---

# SCENE 1: The Arena of Five
*Role: Opening Hook, Beat 1 Visual, Short #1, and Episode Cover Art*

### 🅰️ 16:9 Widescreen Landscape (YouTube Long Video & Cover Art)

**Unified Prompt (Gemini / ChatGPT / T2V Video Generators):**
> A cinematic 3D digital concept art scene of five stylized humanoid robotic figures standing in a wide circle inside a vast, dark computational laboratory. The figures are sleek and minimalist, each with a smooth, faceless glowing cube for a head. The floor is polished, highly reflective dark obsidian glass with faint illuminated grid lines. Two cooperative figures emit a steady, radiant cyan and teal neon glow, with glowing fiber-optic light filaments connecting their hands. Two predatory figures across the circle pulse with sharp amber and fiery orange electrical embers. A fifth figure glows in rich magenta. Volumetric haze, dramatic cyan-amber chiaroscuro lighting, futuristic cyberpunk minimalism. Camera motion: Slow, smooth cinematic forward push-in (dolly-in) towards the center of the ring while subtle neon energy pulses along the filaments. Wide 16:9 widescreen composition with generous negative space. Strictly no text, letters, or watermarks.

**For Midjourney / Leonardo AI:**
> `Cinematic wide shot of five glowing humanoid robotic entities with minimalist cube heads standing in a circular digital arena, vast dark computational laboratory, reflective dark obsidian glass floor with faint glowing grid, volumetric lighting, cyan neon light connecting cooperative entities, amber electrical sparks emitting from predators, slow cinematic dolly-in camera motion, octane render, 8k, photorealistic depth of field --ar 16:9 --no text, words, watermark, logos, human skin, blur`

**I2V Motion Cue (If animating a generated still):**
> `Slow cinematic forward camera push-in towards the circle of glowing cube-headed figures. Subtle neon energy pulses between their hands. 24fps atmospheric haze.`

---

### 🅱️ 9:16 Vertical Portrait (YouTube Shorts & Instagram Reels)

**Unified Prompt (Gemini / ChatGPT / T2V Video Generators):**
> A dramatic vertical 9:16 mobile composition of a futuristic cybernetic arena. From a low-angle perspective, two sleek humanoid robotic figures with glowing cube heads stand in the immediate lower foreground—one glowing in bright cyan neon, the other sparking with hostile amber electricity. In the background above them, three more cube-headed figures stand in an elevated ring. Towering vertical light beams and fiber-optic filaments shoot straight up toward the dark ceiling mist. Polished obsidian reflective floor. Camera motion: Smooth vertical upward crane tilt, rising slowly from the foreground figures toward the towering illuminated arena above. Center-weighted framing leaving the top 15% and bottom 20% clear for on-screen captions. Widescreen cropped to 9:16 vertical ratio. No text or typography.

**For Midjourney / Leonardo AI:**
> `Low angle vertical shot of glowing minimalist cube-headed robotic figures in a digital arena, one cyan cooperative figure and one amber predatory figure in foreground, towering vertical beams of neon light shooting into dark cybernetic ceiling, reflective obsidian floor, smooth upward tilt camera movement, cinematic lighting, 8k, cyberpunk minimalism --ar 9:16 --no text, labels, watermark, cartoon, low quality`

**I2V Motion Cue (If animating a generated still):**
> `Smooth vertical camera tilt upward from the foreground figures into the towering neon light beams. Subtle electrical sparks drifting upward.`

---

# SCENE 2: The Grudger's Fatal Wall
*Role: Beat 2 Visual & Short #2 ("The Fatal Flaw of the Unforgiving Strategy")*

### 🅰️ 16:9 Widescreen Landscape (YouTube Long Video)

**Unified Prompt (Gemini / ChatGPT / T2V Video Generators):**
> A dramatic narrative sci-fi scene inside a dark futuristic server chamber. In the left foreground, a sleek minimalist robotic figure with a glowing magenta cube head turns its back and erects a wide, jagged, glowing amber computational firewall, cutting itself off completely. On the right, another glowing cube-headed figure reaches out helplessly with a soft cyan light pulse that bounces harmlessly off the amber barrier and shatters. Dark obsidian reflective surfaces, cool blue atmospheric mist contrasted with the harsh fiery amber of the barrier, dramatic chiaroscuro lighting. Camera motion: Slow horizontal tracking shot gliding from left to right along the jagged amber wall as sparks pulse across the barrier. Cinematic 16:9 widescreen, shallow depth of field. Strictly no text or letters.

**For Midjourney / Leonardo AI:**
> `Cinematic widescreen medium shot of a minimalist cube-headed robotic figure glowing in deep magenta, turning its back and summoning a wide jagged amber energy firewall, soft cyan light pulse bouncing off the barrier, dark cybernetic chamber, volumetric fog, slow horizontal slider camera movement, octane render, 8k --ar 16:9 --no text, typography, watermark, logo, cartoon`

**I2V Motion Cue (If animating a generated still):**
> `Slow horizontal camera pan from left to right. Jagged amber barrier pulses with sharp electrical sparks while the magenta figure remains motionless.`

---

### 🅱️ 9:16 Vertical Portrait (YouTube Shorts & Instagram Reels)

**Unified Prompt (Gemini / ChatGPT / T2V Video Generators):**
> A striking vertical 9:16 sci-fi narrative scene. A monolithic, towering amber computational energy wall rises straight up through the center of the vertical frame like an impenetrable fortress. In the lower-left corner, a sleek robotic figure with a glowing magenta cube head stands in sharp silhouette, turned away in permanent defiance. On the other side of the barrier, faint cyan ripples strike the wall and dissolve into falling pixel dust. Deep black background, intense amber neon glow illuminating the vertical mist. Camera motion: Slow, dramatic vertical tilt pan moving upward along the towering amber energy wall, emphasizing its overwhelming height and finality. Centered vertical framing optimized for mobile screens. No text or watermarks.

**For Midjourney / Leonardo AI:**
> `Vertical dramatic low angle shot of a towering monolithic amber energy wall dividing two cybernetic zones, silhouette of a magenta cube-headed robot with back turned in lower corner, cyan light ripples hitting the wall, dark server abyss, slow upward camera pan, high contrast, 8k, cinematic minimalism --ar 9:16 --no text, words, watermark, logos, distorted anatomy`

**I2V Motion Cue (If animating a generated still):**
> `Slow vertical pan rising up the towering amber firewall. Electrical sparks cascade down the surface as cyan ripples dissolve.`

---

# SCENE 3: The Cooperative Society Network
*Role: Beat 3 Visual & Short #3 ("Why Winning Every Battle Loses the War")*

### 🅰️ 16:9 Widescreen Landscape (YouTube Long Video)

**Unified Prompt (Gemini / ChatGPT / T2V Video Generators):**
> A breathtaking wide-angle sci-fi digital artwork showing a thriving digital society of dozens of glowing cube-headed cybernetic figures. They stand together on elevated geometric platforms made of translucent computational glass. Brilliant streams of glowing cyan and turquoise light pulse between them like a living neural network, symbolizing mutual trust and emergent cooperation. Far below in the dark shadowed chasms, a few isolated figures pulse dimly with flickering, solitary amber sparks, unable to access the network. Epic scale, cinematic sci-fi minimalism, volumetric light rays, deep dark atmosphere with glowing neon accents. Camera motion: Majestic slow sweeping orbital crane shot gliding across the illuminated network as continuous light pulses travel between the agents. Cinematic 16:9 widescreen, strictly no text or numbers.

**For Midjourney / Leonardo AI:**
> `Epic cinematic wide shot of a thriving multi-agent civilization, dozens of glowing cube-headed cybernetic figures on elevated glass platforms interconnected by brilliant cyan neon neural filaments, isolated amber figures flickering below in dark chasms, majestic sweeping aerial camera glide, volumetric god rays, 8k resolution, photorealistic concept art --ar 16:9 --no text, labels, watermark, cartoon, noise`

**I2V Motion Cue (If animating a generated still):**
> `Slow sweeping orbital camera glide over the glowing cyan network. Pulses of light travel continuously along the connecting filaments.`

---

### 🅱️ 9:16 Vertical Portrait (YouTube Shorts & Instagram Reels)

**Unified Prompt (Gemini / ChatGPT / T2V Video Generators):**
> An awe-inspiring vertical 9:16 composition depicting extreme multi-tiered digital architecture. In the lower third of the mobile frame, a dark shadowy abyss contains isolated, lonely robotic figures flickering with dim, dying amber sparks. Rising dramatically into the upper two-thirds of the frame are towering, luminous geometric platforms populated by dozens of interconnected cybernetic figures glowing in radiant cyan and teal. Cascades of vertical light filaments connect the cooperative society above. Camera motion: Dynamic vertical ascending push-in, rising smoothly from the dark solitary abyss at the bottom toward the brilliant glowing metropolis of cooperation above. Center-weighted vertical framing, cinematic contrast, no text.

**For Midjourney / Leonardo AI:**
> `Vertical shot of a multi-tiered cybernetic society, dark bottom abyss with isolated dim amber figures, towering glowing upper spires with dozens of interconnected cyan cube-headed figures, vertical light streams, smooth ascending camera motion, epic scale, high contrast, 8k --ar 9:16 --no text, watermark, logo, blurry, oversaturated`

**I2V Motion Cue (If animating a generated still):**
> `Smooth vertical camera ascension moving from the dark amber figures at the bottom up into the brilliant glowing cyan network above.`

---

# SCENE 4: The Glitch in the Wire
*Role: Beat 4 Outro & Episode 3 Teaser ("Noise & Miscommunication")*

### 🅰️ 16:9 Widescreen Landscape (YouTube Long Video)

**Unified Prompt (Gemini / ChatGPT / T2V Video Generators):**
> A dramatic macro close-up of a sleek, glowing neon cyan fiber-optic data cable running horizontally through a dark computational environment. In the center of the frame, a violent digital glitch causes the smooth cyan light to fracture and burst into jagged red, amber, and pixelated electrical static. Tiny holographic fragments scatter into the dark background. Macro lens, intense shallow depth of field, sharp foreground focus, dramatic contrast between peaceful cyan data and chaotic crimson corruption. Camera motion: Slow horizontal slider tracking along the glowing cable as the glitch violently flickers and bursts with electrical sparks. Cinematic 16:9 widescreen, no text or typography.

**For Midjourney / Leonardo AI:**
> `Macro cinematic close-up of a glowing cyan fiber-optic cable violently fracturing into jagged red and amber digital glitch noise and pixel fragments, dark cybernetic server room, shallow depth of field, slow slider camera move, sparks bursting, dramatic sci-fi tension, 8k --ar 16:9 --no text, watermark, logo, cartoon`

**I2V Motion Cue (If animating a generated still):**
> `Slow horizontal camera drift along the cable. Rapid electrical glitch flicker with sparks bursting and drifting into darkness.`

---

### 🅱️ 9:16 Vertical Portrait (YouTube Shorts & Instagram Reels)

**Unified Prompt (Gemini / ChatGPT / T2V Video Generators):**
> A dramatic vertical 9:16 macro shot. A luminous neon cyan fiber-optic data cable runs vertically straight down the center of the phone screen against an obsidian black void. Halfway down the screen, a sudden violent digital corruption erupts—the clean cyan line shatters into jagged red, orange, and amber pixel static and electrical sparks that rain downward. Macro lens, intense bokeh in the background, sharp electrical detail. Camera motion: Slow vertical pull-back with rapid micro-glitch jitter as crimson sparks shower down the frame. Vertical composition centered perfectly for mobile viewing. No text or watermarks.

**For Midjourney / Leonardo AI:**
> `Vertical macro shot of a glowing cyan data cable running down the center of the frame, violently snapping into red and amber pixel glitch fragments and raining sparks, dark void, shallow depth of field, micro-jitter camera shake, 8k --ar 9:16 --no text, words, watermark, logos, blur`

**I2V Motion Cue (If animating a generated still):**
> `Slow vertical pull-back with sudden micro-glitch shutter and electrical sparks cascading down the frame.`

---

## 🚀 Quick Execution Summary

1. **For YouTube Long-Form Video**: Copy prompts from section **`🅰️ 16:9 Widescreen Landscape`**.
2. **For Shorts & Instagram Reels**: Copy prompts from section **`🅱️ 9:16 Vertical Portrait`**.
3. **If using Gemini or ChatGPT**: Paste the top descriptive block (they automatically understand aspect ratios and camera motion).
4. **If using Midjourney or Leonardo**: Copy the `Prompt` + `--ar 16:9` (or `--ar 9:16`) and add the `--no` negative block.
5. **If animating with Hailuo / Kling / PixVerse**: Use the **I2V Motion Cue** to set camera movement for your generated image.
