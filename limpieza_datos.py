from CleaningData.clean_main import clean_total 
import platform

so = platform.system()
if so == 'Windows':
    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    print('Esta parte del código sirve en en WSL o Linux para obtener el puntaje de daños, si se corre en Windows el puntaje de daños va a ser 0. Tener muy en cuencta el sistema operativo')
    print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
# El path toca cambiarlo 
path = r'../flota_eq_2025_06.xlsx'
name_out = 'flota_eq_2025_06clean.csv'
clean_total(path, name_out, ubicacion_doble=True)
