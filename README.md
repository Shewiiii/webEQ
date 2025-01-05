**I decided to pause that project for now, and I don't know if I will continue to maintain it in the future. I don't completely agree anymore on what I've done or written on the website, and I'm not motivated to update it.
But if you still want to use it, I strongly recommend you using the default AutoEQ algorithm: an agressive EQ above 10Khz is completely pointless because of both HRTF and HpTF effects.**

Simple website to auto EQ IEMs/TWS, in line with the new standards.  
Website: https://webEQ.pythonanywhere.com

## Requirements
One of the following compatible softwares/apps:
- [Equalizer APO](https://sourceforge.net/projects/equalizerapo/) (Windows, free)
- [Wavelet](https://play.google.com/store/apps/details?id=com.pittvandewitt.wavelet) (Android, free)
- [Poweramp Equalizer](https://play.google.com/store/apps/details?id=com.maxmpz.equalizer) (Android, paid)
- [Peace](https://sourceforge.net/projects/peace-equalizer-apo-extension/), but only works with peak filters for now, so with Lochbaum's algorithm (Windows, free)
- [HQPlayer](https://signalyst.com/consumer/) 4 or 5, via the in-built IIR plugin (Windows/Linus/macOS, paid)
- [Moondrop link](https://moondroplab.com/en/download), supported by AutoEQ's library, the "default" algorithm (Android, free)

## Features
- EQ an IEM (and a few headphones) to a given target
- Tweak the EQ to fit your needs
- EQ an IEM to another IEM (click on the |∀・) kaomoji)
- Save and share the EQ you have generated with a permalink (eg. https://webeq.pythonanywhere.com/results/1)
- Pretty embeds on Discord :D
  
![embed example](https://cdn.discordapp.com/attachments/1193547778689863682/1234944924487778344/embed_example.png?ex=66329396&is=66314216&hm=3651bb4925cfdfec112f938c214622d4474665b3c1320d26a75e16af1e3138c1&)

## Important notes !
- First, this website is intended for people new to EQ. All EQ profiles are auto-generated, and thus can't be very accurate. You will get better results if you EQ manually, using my "frequency_response" and "targets" repo, along with [Listener's 5128 database](https://listener800.github.io/5128) for example ! (You can vizualize what you are doing, EQ and listen to a song of your choice at the same time etc.)

- Second, lower your excpectations with the IEM to IEM EQ feature: it will NOT sound like the actual IEM, especially in the treble ! Though, you can get a more accurate EQ after manual adjustements

- Last but not least, thanks for using my website, feel free to give me a feedback ! <3
