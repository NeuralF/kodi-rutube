# RUTUBE for Kodi

A small Kodi video add-on for [rutube.ru](https://rutube.ru), built on the site's public JSON API. It needs no account and no API key, and has no dependencies beyond Kodi itself.

- **Search**, with the last 10 queries kept in the main menu.
- **Categories**, the same list as on the site.
- **Channel** of any video's author, from the context menu.
- **Paging** through long lists.
- **Playback** of HLS through InputStream Adaptive when it is installed, with a configurable resolution cap. Without it, Kodi's built-in HLS player is used.
- **Languages:** English and Russian. Other languages fall back to English.

Requires Kodi 19 (Matrix) or newer. Tested on Kodi 21 (Omega), LibreELEC on a Raspberry Pi 3.

## Install

Download `plugin.video.rutube-1.0.0.zip` from [Releases](https://github.com/NeuralF/kodi-rutube/releases), then use *Add-ons → Install from zip file*. Enable *Unknown sources* first, if it's off.

The zip that GitHub offers under *Code → Download ZIP* will not install: Kodi needs the folder inside to be named `plugin.video.rutube`.

To build the zip yourself:

```sh
git archive --prefix=plugin.video.rutube/ -o plugin.video.rutube.zip HEAD
```

## Notes

- Some videos are geo-restricted or need a login on the site. The add-on then shows "Video is not available".
- The API is undocumented and can change. Please open an issue if something breaks.

Not affiliated with RUTUBE.

## License

MIT
