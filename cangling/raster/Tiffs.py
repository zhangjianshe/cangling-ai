from osgeo import gdal, osr
import numpy as np

gdal.UseExceptions()

def assignImageColorTable(fileName, color_table_entries=None):
    # Use GA_Update to modify an existing file
    ds = gdal.Open(fileName, gdal.GA_Update)
    if ds is None:
        print(f"Could not open {fileName}")
        return

    ct = gdal.ColorTable()

    if color_table_entries:
        for idx, rgba in color_table_entries.items():
            ct.SetColorEntry(idx, rgba)
    else:
        # Default fallback palette
        ct.SetColorEntry(0, (255, 0, 0, 255))    # Red
        ct.SetColorEntry(1, (0, 255, 0, 255))    # Green
        ct.SetColorEntry(2, (0, 0, 255, 255))    # Blue
        ct.SetColorEntry(3, (255, 255, 0, 255))  # Yellow

    band = ds.GetRasterBand(1)
    band.SetRasterColorTable(ct)
    band.SetRasterColorInterpretation(gdal.GCI_PaletteIndex)

    # Clean up
    ds.FlushCache()
    ds = None
    print(f"Success: Assigned color table to {fileName}")

def test():
    width, height = 1000, 1000
    driver = gdal.GetDriverByName('GTiff')
    # Using your Cangling path
    output_file = "/mnt/cangling/devdata/personal/1/test1/123.tif"

    # Create 1-band Byte image
    ds = driver.Create(output_file, width, height, 1, gdal.GDT_Byte)

    # Beijing-ish coordinates (WGS84)
    pixel_size = 0.01
    x_left, y_top = 116.4, 39.9
    ds.SetGeoTransform([x_left, pixel_size, 0, y_top, 0, -pixel_size])

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    ds.SetProjection(srs.ExportToWkt())

    # Create dummy data using the palette indices
    data = np.zeros((height, width), dtype=np.uint8)
    data[0:500, 0:500] = 0
    data[0:500, 500:1000] = 1
    data[500:1000, 0:500] = 2
    data[500:1000, 500:1000] = 3

    band = ds.GetRasterBand(1)
    band.WriteArray(data)

    # Close dataset to ensure it's written before assignImageColorTable opens it
    ds = None
    print(f"Created initial file: {output_file}")

    # Now test the assignment function
    custom_palette = {
        0: (255, 0, 0, 255),
        1: (0, 255, 0, 255),
        2: (0, 0, 255, 255),
        3: (255, 255, 0, 255)
    }
    assignImageColorTable(output_file, custom_palette)

if __name__ == "__main__":
    output_file = "/mnt/cangling/devdata/personal/1/test1/123.tif"
    custom_palette = {
        0: (255, 0, 0, 255),
        1: (0, 255, 0, 255),
        2: (0, 0, 255, 255),
        3: (255, 255, 0, 255)
    }
    assignImageColorTable(output_file,custom_palette)