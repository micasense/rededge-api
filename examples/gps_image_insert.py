import click
import re
import csv

@click.group()
def main():
    pass

@main.command()
@click.option('--input_path', default=None, help='Path of file to have flight image numbers inserted (original file is kept unmodified')
@click.option('--output_path', default=None, help='Path to save new file output with image numbers inserted')
def create_image_location_file(input_path, output_path):
    img_counter = 0

    with open(input_path, 'rb') as f:        
        text_reader = csv.reader(f, delimiter=' ')
        for row in text_reader:
            date_to_img = re.match('\d{4}.\d{2}.\d{2}', row[0])
            if date_to_img:
                g = open(output_path, 'ab')
                text_writer = csv.writer(g, delimiter=' ')
                for n in range(1, 6):
                    text_writer.writerow([('IMG_%04d_%d.tif' % (img_counter, n))]
                                                               + [row[4]]
                                                               + [row[5]]
                                                               + [row[9]])
                g.close()
                img_counter += 1

if __name__ == "__main__":
    main()