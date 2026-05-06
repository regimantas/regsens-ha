<p align="center">
  <img src="custom_components/regsens/brand/logo.png" alt="RegSens logo" width="320">
</p>

# RegSens Home Assistant Integration

HACS-ready custom integration for RegSens devices.

The integration polls the configured RegSens endpoint and dynamically adds newly discovered entities during the regular poll cycle.

## Install With HACS

If HACS is not installed yet, install and configure HACS first: <https://www.hacs.xyz/docs/use/>.

1. In Home Assistant, open HACS.
2. Open the three-dot menu and choose **Custom repositories**.
3. Add `https://github.com/regimantas/regsens-ha`.
4. Select **Integration** as the category.
5. Click **Add**.
6. Find **RegSens** in HACS and download it.
7. Restart Home Assistant.
8. Go to **Settings > Devices & services > Add integration > RegSens**.
9. Enter your RegSens API URL and API key.
