---
title: Building a darkroom timer
date: 2021-12-29
image: IMG_6833.jpg
tags:
  - photography
  - film
  - darkroom
  - arduino
  - wood-working
---

# YouTube video:
<iframe width="560" height="315" src="https://www.youtube.com/embed/vmfK1WbUyfw" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>


# Project

This is a Gralabs darkroom timer, probably from the 1950s or 60s. 

<v-img src="gralabs s-l1600.jpg" alt="bar" :dirp="dir"></v-img>

The timer is used to turn on and off the enlarger at precise times.  You need to do this to get the right exposure (and with test strips to figure out what that correct exposure time should be).

Of course I looked at this elegant and time-tested design (which is still being made and sold today in essentially unchanged form), and thought, yeah.  I can do better than that.

So I build my own timer.

<v-img src="IMG_6833.jpg" alt="bar" :dirp="dir"></v-img>

It has switches for manually controlling the enlarger and safelight.  The LED display and rotary knob/button change the timer interval.

To start the timer, I've used a big red button from an arcade machine.  The timer also supports early cancellation, and can be held down for overtime.  I had planned to add a foot pedal as well, but the unshielded wiring was causing random triggers of the start button, so I dropped that feature for now.


This project started out as a sketch in my notebook as I figured out what the essential functionality I needed as, and how best to implement it.

I wanted the exterior to be fancier than my usual black boxes, so I made a oak box and used a piece of brass for the faceplate.

The innards include a relay module and 5v power supply, an Arduino micro-controller, and a custom circuit board that provides easy breakouts for the other components, and includes the beeper.  

Writing the [arduino code](https://github.com/brianssparetime/darkroom_timer) turned out to be more complicated than I thought.  I wound up learning a bit about interrupts (which I use for the start button), as well as button debouncing (still a bit of an issue).

Would it have been simpler and faster to just buy a timer?  Certainly.  Cheaper?  Probably.

But this project was as more about the fun of making and learning, and I'm happy with how it turned out.

That said, I'm already thinking about an improved second version....

I'd like to:

 - support additional settings on the LCD, including expontential timers, preset time recipes for film developing, and more
 - have better internal separation between the AC and arduino sides.  Perhaps move the AC part to a floor box instead of having everything integrated.
 - move to a more capable microcontroller, where programming menus and state machines isn't so hellish

