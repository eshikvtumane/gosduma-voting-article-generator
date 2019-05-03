from PIL import Image, ImageDraw, ImageFont


class GosDumaScreen(object):
    def __init__(self, vote_date, vote_for, vote_against, vote_abstain, result):
        if result:
            self._image_new = Image.new('RGB', (500, 280), (0, 0, 123))
        else:
            self._image_new = Image.new('RGB', (500, 280), (195, 20, 1))
        self.image = ImageDraw.Draw(self._image_new)
        self.font = ImageFont.truetype('Arial.ttf', 30)

        self.image.text((35, 10), "Количественное голосование", font=self.font)
        self.image.text((80, 40), "Государственная Дума", font=self.font)
        self.image.text((100, 75), vote_date, font=self.font)

        self.write_line(offset=3, count_dots=30, name_line='За', total=vote_for,
                        percent=self._calc_percent(vote_for))
        self.write_line(offset=4, count_dots=22, name_line='Против',
                        total=vote_against, percent=self._calc_percent(vote_against))
        self.write_line(offset=5, count_dots=9, name_line='Воздержалось',
                        total=vote_abstain, percent=self._calc_percent(vote_abstain))

        total_quantity = int(vote_for) + int(vote_against) + int(vote_abstain)
        self.write_line(offset=6, count_dots=13, name_line='Голосовало',
                        total=total_quantity, percent=self._calc_percent(total_quantity))

        if result:
            self.image.text((120, 40 + (30 * 7) + 3), 'РЕШЕНИЕ ПРИНЯТО', font=self.font)
        else:
            self.image.text((100, 40 + (30 * 7) + 3), 'РЕШЕНИЕ НЕ ПРИНЯТО', font=self.font, fill=(252, 163, 59, 255))

    def _calc_percent(self, value):
        return (float(value) * 100) / 450

    def write_line(self, offset, count_dots, name_line, total, percent):
        self.image.text((10, 40 + (30 * offset)), name_line + '.' * count_dots, font=self.font)

        self.image.text((290 + self._value_offset(int(total)), 40 + (30 * offset)), '%s ч.' % total, font=self.font)
        self.image.text((390 + self._value_offset(float(percent)), 40 + (30 * offset)), '{0}%'.format("%.1f" % round(percent, 1)), font=self.font)

    def _value_offset(self, value):
        text_result_offset = 0
        if 9 < value < 100:
            text_result_offset += 20
        elif 0 <= value < 10:
            text_result_offset += 35

        return text_result_offset

    def save_png(self, name='pil_red'):
        name = '{0}.png'.format(name)
        self._image_new.save(name)
        return name
