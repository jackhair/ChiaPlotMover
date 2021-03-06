# ChiaPlotMover
Schedules a job to periodically move Chia `.plot` files from a staging drive to a destination drive.

**Disclaimer:** I have never written Python before, so this is very much a learning exercise.

![image](https://user-images.githubusercontent.com/357712/116839114-dc4d8500-ab85-11eb-9b8e-dd84a7abacaa.png)

#### Features
- [x] Moves `.plot` files from staging to destination drive
- [x] Set custom interval for job to run
- [x] Sends updates to Discord using Webhooks

#### TODO
- [ ] Check that destination drive has space for plot
- [ ] Use an array of destination drives

## Installation

1. Install the latest version of Python: https://www.python.org/downloads/
2. Download the repo with `git clone` or download `.zip`
3. Move into downloaded folder with `cd`
4. Install requirements `pip install -r requirements.txt`
5. Rename `.env.sample` to `.env` and configure (see Config below)
6. Run with `python start.py`

## Config

- `INTERVAL` - Interval in seconds to run the job. Example: `INTERVAL=600`
- `STAGING` - Directory where files are staged. Example: `STAGING=D:/`
  - You can use folders too, just make sure they exist. Example: `STAGING=D:/plots/`
- `DESTINATION` - Directory where files will be moved to. Example: `DESTINATION=E:/`
  - You can use folders here too, see above example.
- `DISCORD_WEBHOOK_URL` - _[OPTIONAL]_ Webhook URL for sending messages to Discord
  - https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks
