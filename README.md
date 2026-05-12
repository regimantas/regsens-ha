<p align="center">
  <img src="custom_components/regsens/brand/logo.png" alt="RegSens logo" width="320">
</p>

# RegSens Home Assistant Integration

## English

RegSens is a HACS-ready custom integration for Home Assistant.

The integration connects to the official RegSens API, receives live device updates over WebSocket, and keeps a periodic poll as a fallback resync.
It supports RegSens sensors, binary sensors, switches, numbers, RGB lights, sensor device classes, battery-powered PIR motion sensors, and ESP-NOW child devices routed through a claimed RegSens hub. Sleeping battery sensors keep their last value visible while controllable entities still show offline when the device sleeps.

### Install with HACS

If HACS is not installed yet, install and configure HACS first: <https://www.hacs.xyz/docs/use/>.

1. In Home Assistant, open HACS.
2. Open the three-dot menu and choose **Custom repositories**.
3. Add `https://github.com/regimantas/regsens-ha`.
4. Select **Integration** as the category.
5. Click **Add**.
6. Find **RegSens** in HACS and download it.
7. Restart Home Assistant.
8. Go to **Settings > Devices & services > Add integration > RegSens**.
9. Enter your RegSens API key. The server address is built into the integration.

### Add Devices

Add and manage RegSens devices at <https://api.regsens.com>.

## Lietuviškai

RegSens yra HACS paruošta Home Assistant integracija.

Integracija jungiasi prie oficialaus RegSens API, gyvai gauna įrenginių pokyčius per WebSocket ir palieka periodinį polling kaip atsarginį persinchronizavimą.
Ji palaiko RegSens jutiklius, dvejetainius jutiklius, jungiklius, skaičių valdiklius, RGB šviesas, jutiklių klases, baterinius PIR judesio jutiklius ir ESP-NOW child įrenginius per claim'intą RegSens hub'ą. Miegantys bateriniai jutikliai palieka paskutinę reikšmę matomą, o valdomi elementai vis tiek rodomi neprisijungę, kai įrenginys miega.

### Diegimas per HACS

Jeigu HACS dar neįdiegtas, pirmiausia įdiekite ir sukonfigūruokite HACS: <https://www.hacs.xyz/docs/use/>.

1. Home Assistant aplinkoje atidarykite HACS.
2. Atidarykite trijų taškų meniu ir pasirinkite **Custom repositories**.
3. Įveskite `https://github.com/regimantas/regsens-ha`.
4. Kategorijoje pasirinkite **Integration**.
5. Spauskite **Add**.
6. HACS lange suraskite **RegSens** ir atsisiųskite integraciją.
7. Perkraukite Home Assistant.
8. Eikite į **Settings > Devices & services > Add integration > RegSens**.
9. Įveskite RegSens API raktą. Serverio adreso įvesti nereikia, jis jau įrašytas integracijoje.

### Įrenginių pridėjimas

RegSens įrenginius pridėkite ir valdykite adresu <https://api.regsens.com>.
