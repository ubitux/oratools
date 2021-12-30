# OpenRA tooling

This repository contains some experimental tooling for working with OpenRA
replay/network code.

After running `make` and entering the virtual env with `. venv/bin/activate`,
`ora-tool` with the following tools:

- `ora-tool buildorder`: try to figure the build orders from the specified
  replay(s); doesn't work that great because it requires the complete game
  emulation
- `ora-tool chat`: display chat events from the specified replay(s)
- `ora-tool trace`: demux (split into packets) and decode (extract orders from
  packets) from the specified replay(s); useful for getting a debugging trace

**Warning**: on macOS, pulling the Pillow package from pip can be challenging.
Make sure libjpeg is installed on the system (using [brew][brew-website]: `brew
install jpeg`).

[brew-website]: https://brew.sh

## Examples

### Build Order
```
☭ ora-tool buildorder ~/.config/openra/Replays/ra/release-20200503/RAGL-S09-MASTER-GROUP-GOA-ILM-G1.orarep
Replay: /home/user/.config/openra/Replays/ra/release-20200503/RAGL-S09-MASTER-GROUP-GOA-ILM-G1.orarep
i like men:
  00:02.280 → 00:10.680: powr
  00:11.160 → 00:24.600: tent
  00:28.800 → 00:42.360: tent
  00:29.760 → 01:19.200: proc
gggggggggggggggg:
  00:02.640 → 00:10.920: powr
  00:11.760 → 00:25.080: barr
  00:14.040 → 01:01.320: proc
  00:14.160 → 01:46.320: proc
  00:14.400 → 01:56.280: powr
  01:13.200 → 02:23.520: ftur
```

### Chat
```
☭ ora-tool chat ~/.config/openra/Replays/ra/release-20190314/RAGL-S08-MASTER-GROUP-ZXG-UPS-G2.orarep
Replay: /home/user/.config/openra/Replays/ra/release-20190314/RAGL-S08-MASTER-GROUP-ZXG-UPS-G2.orarep
[global]  <^^ZxGanon^^|RV>  okay
[global]  <^^ZxGanon^^|RV>  ich nehm die map hier
[global]               <U>  k
[global]               <U>  glhf
[global]  <^^ZxGanon^^|RV>  nl hf
[global]               <U>  gg
[global]  <^^ZxGanon^^|RV>  gg
```

### Trace

```
☭ ora-tool trace --filter Fields ~/.config/openra/Replays/ra/release-20200503/RAGL-S09-MASTER-GROUP-AMO-HAP-G1.orarep
[...]
PKT client:3 frame:632 datalen:5
PKT client:12 frame:636 datalen:0
PKT client:12 frame:632 datalen:5
PKT client:6 frame:636 datalen:0
PKT client:6 frame:632 datalen:5
PKT client:35 frame:635 datalen:0
PKT client:35 frame:631 datalen:5
PKT client:16 frame:637 datalen:0
PKT client:16 frame:633 datalen:5
PKT client:22 frame:637 datalen:127
  ORD [Fields] field:CreateGroup info:
{'extra_actors': (98, 100, 102, 96, 94), 'subject_id': 4}
PKT client:22 frame:633 datalen:5
PKT client:14 frame:637 datalen:0
PKT client:14 frame:633 datalen:5
PKT client:33 frame:637 datalen:0
PKT client:33 frame:633 datalen:5
PKT client:26 frame:637 datalen:0
PKT client:26 frame:633 datalen:5
PKT client:19 frame:637 datalen:0
PKT client:19 frame:633 datalen:5
PKT client:3 frame:637 datalen:92
  ORD [Fields] field:AttackMove info:
{'cell': 63970816, 'sub_cell': 0, 'subject_id': 95}
PKT client:3 frame:633 datalen:5
PKT client:12 frame:637 datalen:0
PKT client:12 frame:633 datalen:5
PKT client:6 frame:637 datalen:0
PKT client:6 frame:633 datalen:5
PKT client:35 frame:636 datalen:0
PKT client:35 frame:632 datalen:5
PKT client:16 frame:638 datalen:0
PKT client:16 frame:634 datalen:5
PKT client:22 frame:638 datalen:0
PKT client:22 frame:634 datalen:5
PKT client:14 frame:638 datalen:0
[...]
```
