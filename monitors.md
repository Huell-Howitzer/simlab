Ensuring GNOME Login Screen Appears on the Correct Monitor

Understanding the Issue

By default, GDM (GNOME Display Manager) picks one display to show the login screen, often arbitrarily in multi-monitor setups ￼. In a dual-monitor scenario (e.g. a desktop with two screens or a laptop plus external display), GDM might place the login prompt on the wrong screen – which becomes a problem if that screen is not active or connected (such as when using a KVM switch in a conference room). To fix this, we need to configure GDM to use the desired monitor (or mirror both) for the login screen.

Method 1: Configure GDM with monitors.xml (Works for X11 and Wayland)

GNOME stores display settings (position, resolution, primary monitor, etc.) in a file called ~/.config/monitors.xml for each user. GDM will honor a similar file in its own config directory. We can leverage this to force the login screen onto a specific monitor or mirror displays:
	1.	Set up Displays in GNOME: Log into your GNOME desktop session and open Settings > Displays. Arrange the monitors as you want them at login:
	•	Mark the monitor that should show the login prompt as Primary (drag the black top bar in the display diagram to that monitor).
	•	(Optional) If you prefer the login screen to appear on all monitors (mirrored), enable Mirror Displays in the display settings. This will clone the output to both screens at login.
	•	Apply the settings. This updates your ~/.config/monitors.xml file with the new layout (including which monitor is primary, or a single combined logical monitor if mirroring is on).
	2.	Copy monitors.xml to GDM’s config: Use Terminal to copy your monitors configuration to the GDM user’s directory. On Red Hat-based systems (Fedora/RHEL), the GDM user’s home is /var/lib/gdm, whereas on Ubuntu/Debian it’s /var/lib/gdm3. For RHEL/Fedora, run:

sudo cp ~/.config/monitors.xml /var/lib/gdm/.config/monitors.xml
sudo chown gdm:gdm /var/lib/gdm/.config/monitors.xml

This places your display layout into GDM’s config and ensures it’s owned by the gdm user (so GDM can read it) ￼. (If you were on Ubuntu, you’d use the gdm3 path instead ￼, but for Red Hat it’s gdm.)

	3.	Restart GDM: Reboot the machine or restart GDM (sudo systemctl restart gdm) to apply the changes. On the next boot/login screen, GDM should apply those monitor settings. The login screen will now appear on the designated primary monitor (or on both monitors if you enabled mirroring) ￼ ￼.

Notes:
	•	Matching X11/Wayland Environment: Make sure the monitors.xml you copied was generated in the same display backend that GDM uses. In other words, if GDM runs on Wayland by default (as is typical on modern GNOME with open-source drivers), use a GNOME session on Wayland to set up displays. If GDM is using X11 (common if you have NVIDIA drivers or manually disabled Wayland), use an X11 session to generate the monitors.xml. A monitors.xml from Wayland won’t be recognized under X11 GDM, and vice versa ￼ ￼. If you’re unsure, you can check your current session type with echo $XDG_SESSION_TYPE. (You can force GDM to use X11 by setting WaylandEnable=false in /etc/gdm/custom.conf, but this usually isn’t necessary if you follow the above step correctly ￼.)
	•	Verification: After copying, you can open /var/lib/gdm/.config/monitors.xml to confirm it contains the correct monitor names and has <primary>yes</primary> on the intended display ￼. Also ensure there are no stale or conflicting older config files.

Using the monitors.xml approach is the most robust and does not require a user to be logged in for the setting to take effect – GDM will load this on startup. (In fact, GDM/mutter ignores any static X11 config for monitor layout; it relies on monitors.xml or its own logic ￼.)

Method 2: Mirror or Single-Monitor Mode at Login (Optional)

If your goal is to guarantee the login prompt is always visible, you might choose to have GDM mirror the displays or only enable one screen at login, regardless of your extended layout in the user session. There are two ways to achieve this:
	•	Mirrored Displays at GDM: As mentioned above, setting your displays to “Mirror” before copying the config will make GDM output the login screen on all connected monitors simultaneously. This way, even if one monitor is disconnected or turned off, the other should still show the full login interface. Keep in mind the resolution will usually default to the primary monitor’s resolution and aspect ratio, so the secondary screen might have letterboxing or scaled output. (This is generally fine for a login prompt.) GDM currently has no built-in toggle to mirror by itself – using the monitors.xml trick is the way to enforce it ￼.
	•	Single-Monitor (Disable one display): Alternatively, you can configure your monitors such that one of them is turned off in the GDM layout. For example, in your GNOME Displays settings, you might disable the secondary screen (some systems allow turning off an output entirely). If you then copy that configuration to GDM, the login screen will only activate the one monitor that is on. This ensures the prompt isn’t hidden on a non-visible screen. However, use this with caution – if that “disabled” monitor becomes the only one present (e.g. in a different setup), you could end up with no active display at GDM. In most cases, mirroring or setting the correct primary is safer.

Method 3: Advanced Scripting Solutions (Dynamic Approach)

If your setup changes frequently or you want an automated solution, you can use scripts or systemd rules to detect the active monitor and adjust the display outputs for GDM on the fly. These approaches are more complex and generally only recommended if the static monitors.xml method doesn’t cover your needs:
	•	Systemd Pre-start Script: You can create a systemd override for the GDM service to run a custom script before GDM launches. For example, create a drop-in file at /etc/systemd/system/gdm.service.d/override.conf with contents:

[Service]
ExecStartPre=/usr/local/bin/gdm-display-setup.sh

In /usr/local/bin/gdm-display-setup.sh, you might write logic to check connected displays and run xrandr commands if on X11. For instance, to force a particular monitor on and others off:

#!/bin/bash
export DISPLAY=:0
# Example: turn off DP-2 and enable DP-1 as primary
xrandr --output DP-2 --off --output DP-1 --auto --primary

Make sure to chmod +x this script. The ExecStartPre will run as root before GDM starts the graphical login ￼. This can, for example, turn off an undesired output or clone displays every boot. (Note: On Wayland GDM, xrandr won’t work – this only applies if GDM is using Xorg. There isn’t a straightforward equivalent for Wayland, which is why the monitors.xml method is preferred in that case.)

	•	Udev or loginctl Trigger: Another advanced idea is to use a udev rule to detect when the conference room setup is active (e.g. a specific monitor EDID is connected or another is disconnected) and then copy an appropriate monitors.xml to GDM or adjust settings. For example, a udev rule could watch for the DisplayPort connection of the TV and invoke a script that updates /var/lib/gdm/.config/monitors.xml accordingly. This approach would involve writing udev rules and ensuring they run at the right time (before GDM loads or when switching displays), which can be tricky.
	•	Alternate Display Managers: If GNOME’s GDM proves too rigid, note that other display managers (like LightDM or SDDM) offer easier ways to run display setup scripts at login. For instance, LightDM has a display-setup-script option, and SDDM executes /usr/share/sddm/scripts/Xsetup on the login screen, where you can call xrandr to mirror or reconfigure monitors. Switching to a different DM is a heavy-handed solution, but it can provide more flexibility for multi-monitor handling at the greeter stage.

On-the-fly Monitor Switching at GDM

Currently, GDM does not provide any GUI button or hotkey to cycle the login screen between monitors on the fly. The idea of a keyboard shortcut to “move the login prompt to the other screen” is a known feature request but isn’t implemented as of GNOME 43/44. That means your best bet is to set up one of the above configurations in advance.

If you ever encounter the blank screen issue (login prompt on a non-visible monitor), possible workarounds are:
	•	Use Keyboard Blindly or External Access: If you know the login screen is there, you can press Enter, type your password, and hit Enter to log in without seeing the prompt (or use SSH if enabled to log in remotely). Once logged in, your user display settings will take over and you should get output on the active monitor. This is obviously not ideal, but can get you unstuck in a pinch.
	•	Power Off/Disconnect the Other Monitor: If you physically disconnect or power off the phantom monitor before rebooting into GDM, the system might default to the only connected screen. However, some KVMs present a dummy connection, so the PC may not realize the monitor is gone. In that case, ensuring the GDM config is set properly (as in Method 1 or 2) is the reliable solution.

Summary

For Red Hat Linux (GNOME) systems with fluctuating multi-monitor setups, the most straightforward solution is to configure GDM’s display layout via its monitors.xml. By copying your preferred monitor setup to the GDM config (and setting the correct primary display), you ensure the login screen appears on the active/visible monitor every time ￼ ￼. This approach works under both X11 and Wayland (just remember to use a matching environment for the config) ￼.

If mirroring the login screen or turning off unused displays at login is important, set those preferences in the monitors.xml you provide to GDM. While GDM doesn’t support interactive switching of the greeter display, these configuration tweaks or scripts will cover most scenarios so you aren’t stuck with an invisible login prompt again.

Sources: The GNOME/ArchWiki and Ubuntu docs confirm that copying a properly configured monitors.xml to GDM’s home is the supported way to control login screen monitors ￼ ￼. This technique has been used in Fedora/Red Hat and Ubuntu alike to fix GDM on the wrong screen ￼ ￼. Just be careful to generate the file under the correct session type and give GDM ownership, and you should be all set. Good luck!