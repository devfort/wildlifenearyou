from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.InsertRows(
    table_name = 'faces_facepart',
    columns = [u'id', u'area_id', u'description', u'image'],
    insert_rows = ((470L, 33L, u'Bangs2 Black', u'faceparts/hair_bangs2_black.png'),
 (471L, 33L, u'Bangs2 Blonde', u'faceparts/hair_bangs2_blonde.png'),
 (472L, 33L, u'Bangs2 Blue', u'faceparts/hair_bangs2_blue.png'),
 (473L, 33L, u'Bangs2 Brown Dark', u'faceparts/hair_bangs2_brown_dark.png'),
 (474L, 33L, u'Bangs2 Brown Light', u'faceparts/hair_bangs2_brown_light.png'),
 (475L, 33L, u'Bangs2 Green', u'faceparts/hair_bangs2_green.png'),
 (476L, 33L, u'Bangs2 Orange', u'faceparts/hair_bangs2_orange.png'),
 (477L, 33L, u'Bangs2 Pink', u'faceparts/hair_bangs2_pink.png'),
 (478L, 33L, u'Bangs2 Purple', u'faceparts/hair_bangs2_purple.png'),
 (479L, 33L, u'Bangs2 Red', u'faceparts/hair_bangs2_red.png'),
 (480L, 33L, u'Bangs2 Teal', u'faceparts/hair_bangs2_teal.png'),
 (481L, 33L, u'Bangs Black', u'faceparts/hair_bangs_black.png'),
 (482L, 33L, u'Bangs Blonde', u'faceparts/hair_bangs_blonde.png'),
 (483L, 33L, u'Bangs Blonde Dirty', u'faceparts/hair_bangs_blonde_dirty.png'),
 (484L, 33L, u'Bangs Blue', u'faceparts/hair_bangs_blue.png'),
 (485L, 33L, u'Bangs Brown Dark', u'faceparts/hair_bangs_brown_dark.png'),
 (486L, 33L, u'Bangs Brown Light', u'faceparts/hair_bangs_brown_light.png'),
 (487L, 33L, u'Bangs Green', u'faceparts/hair_bangs_green.png'),
 (488L, 33L, u'Bangs Orange', u'faceparts/hair_bangs_orange.png'),
 (489L, 33L, u'Bangs Pink', u'faceparts/hair_bangs_pink.png'),
 (490L, 33L, u'Bangs Purple', u'faceparts/hair_bangs_purple.png'),
 (491L, 33L, u'Bangs Red', u'faceparts/hair_bangs_red.png'),
 (492L, 33L, u'Black Spikey Red', u'faceparts/hair_black_spikey_red.png'),
 (493L, 33L, u'Mohawk Black', u'faceparts/hair_mohawk_black.png'),
 (494L, 33L, u'Mohawk Blonde', u'faceparts/hair_mohawk_blonde.png'),
 (495L, 33L, u'Mohawk Blue', u'faceparts/hair_mohawk_blue.png'),
 (496L, 33L, u'Mohawk Brown', u'faceparts/hair_mohawk_brown.png'),
 (497L, 33L, u'Mohawk Brown Dark', u'faceparts/hair_mohawk_brown_dark.png'),
 (498L, 33L, u'Mohawk Brown Light', u'faceparts/hair_mohawk_brown_light.png'),
 (499L, 33L, u'Mohawk Green', u'faceparts/hair_mohawk_green.png'),
 (500L, 33L, u'Mohawk Pink', u'faceparts/hair_mohawk_pink.png'),
 (501L, 33L, u'Mohawk Purple', u'faceparts/hair_mohawk_purple.png'),
 (502L, 33L, u'Mohawk Teal', u'faceparts/hair_mohawk_teal.png'),
 (503L, 33L, u'Short Thin Black', u'faceparts/hair_short_thin_black.png'),
 (504L, 33L, u'Short Thin Blonde', u'faceparts/hair_short_thin_blonde.png'),
 (505L, 33L, u'Short Thin Brown', u'faceparts/hair_short_thin_brown.png'),
 (506L,
  33L,
  u'Short Thin Brown Dark',
  u'faceparts/hair_short_thin_brown_dark.png'),
 (507L,
  33L,
  u'Short Thin Brown Light',
  u'faceparts/hair_short_thin_brown_light.png'),
 (508L, 33L, u'Short Thin Red', u'faceparts/hair_short_thin_red.png'),
 (509L, 33L, u'Spikey2 Black', u'faceparts/hair_spikey2_black.png'),
 (510L, 33L, u'Spikey2 Blue', u'faceparts/hair_spikey2_blue.png'),
 (511L, 33L, u'Spikey2 Brown', u'faceparts/hair_spikey2_brown.png'),
 (512L, 33L, u'Spikey2 Brown Dark', u'faceparts/hair_spikey2_brown_dark.png'),
 (513L,
  33L,
  u'Spikey2 Brown Light',
  u'faceparts/hair_spikey2_brown_light.png'),
 (514L, 33L, u'Spikey2 Green', u'faceparts/hair_spikey2_green.png'),
 (515L, 33L, u'Spikey2 Orange', u'faceparts/hair_spikey2_orange.png'),
 (516L, 33L, u'Spikey2 Pink', u'faceparts/hair_spikey2_pink.png'),
 (517L, 33L, u'Spikey2 Purple', u'faceparts/hair_spikey2_purple.png'),
 (518L, 33L, u'Spikey2 Red', u'faceparts/hair_spikey2_red.png'),
 (519L, 33L, u'Spikey2 Teal', u'faceparts/hair_spikey2_teal.png'),
 (520L, 33L, u'Spikey Black', u'faceparts/hair_spikey_black.png'),
 (521L, 33L, u'Spikey Blue', u'faceparts/hair_spikey_blue.png'),
 (522L, 33L, u'Spikey Brown', u'faceparts/hair_spikey_brown.png'),
 (523L, 33L, u'Spikey Brown Dark', u'faceparts/hair_spikey_brown_dark.png'),
 (524L, 33L, u'Spikey Brown Light', u'faceparts/hair_spikey_brown_light.png'),
 (525L, 33L, u'Spikey Green', u'faceparts/hair_spikey_green.png'),
 (526L, 33L, u'Spikey Orange', u'faceparts/hair_spikey_orange.png'),
 (527L, 33L, u'Spikey Pink', u'faceparts/hair_spikey_pink.png'),
 (528L, 33L, u'Spikey Purple', u'faceparts/hair_spikey_purple.png'),
 (529L, 33L, u'Spikey Teal', u'faceparts/hair_spikey_teal.png'),
 (530L, 34L, u'Curly Black', u'faceparts/hair_curly_black.png'),
 (531L, 34L, u'Curly Blonde', u'faceparts/hair_curly_blonde.png'),
 (532L, 34L, u'Curly Blonde Dirty', u'faceparts/hair_curly_blonde_dirty.png'),
 (533L, 34L, u'Curly Blue', u'faceparts/hair_curly_blue.png'),
 (534L, 34L, u'Curly Brown Dark', u'faceparts/hair_curly_brown_dark.png'),
 (535L, 34L, u'Curly Brown Light', u'faceparts/hair_curly_brown_light.png'),
 (536L, 34L, u'Curly Green', u'faceparts/hair_curly_green.png'),
 (537L, 34L, u'Curly Orange', u'faceparts/hair_curly_orange.png'),
 (538L, 34L, u'Curly Pink', u'faceparts/hair_curly_pink.png'),
 (539L, 34L, u'Curly Purple', u'faceparts/hair_curly_purple.png'),
 (540L, 34L, u'Curly Red', u'faceparts/hair_curly_red.png'),
 (541L, 34L, u'Side Black', u'faceparts/hair_side_black.png'),
 (542L, 34L, u'Side Blonde', u'faceparts/hair_side_blonde.png'),
 (543L, 34L, u'Side Brown', u'faceparts/hair_side_brown.png'),
 (544L, 34L, u'Side Brown Dark', u'faceparts/hair_side_brown_dark.png'),
 (545L, 34L, u'Side Gray', u'faceparts/hair_side_gray.png'),
 (546L, 34L, u'Side Gray Dark', u'faceparts/hair_side_gray_dark.png'),
 (547L, 34L, u'Side White', u'faceparts/hair_side_white.png'),
 (548L, 35L, u'Black', u'faceparts/lips_black.png'),
 (549L, 35L, u'Brown Dark', u'faceparts/lips_brown_dark.png'),
 (550L, 35L, u'Brown Light', u'faceparts/lips_brown_light.png'),
 (551L, 35L, u'Green', u'faceparts/lips_green.png'),
 (552L, 35L, u'Orange', u'faceparts/lips_orange.png'),
 (553L, 35L, u'Pink', u'faceparts/lips_pink.png'),
 (554L, 35L, u'Red Bright', u'faceparts/lips_red_bright.png'),
 (555L, 35L, u'Red Dark', u'faceparts/lips_red_dark.png'),
 (556L, 35L, u'Smirk Brown', u'faceparts/lips_smirk_brown.png'),
 (557L, 35L, u'Smirk Brown Dark', u'faceparts/lips_smirk_brown_dark.png'),
 (558L, 35L, u'Smirk Brown Light', u'faceparts/lips_smirk_brown_light.png'),
 (559L, 35L, u'Smirk Green', u'faceparts/lips_smirk_green.png'),
 (560L, 35L, u'Smirk Orange', u'faceparts/lips_smirk_orange.png'),
 (561L, 35L, u'Smirk Pink', u'faceparts/lips_smirk_pink.png'),
 (562L, 35L, u'Smirk Purple', u'faceparts/lips_smirk_purple.png'),
 (563L, 35L, u'Smirk Red', u'faceparts/lips_smirk_red.png'),
 (564L, 35L, u'Smirk Teal', u'faceparts/lips_smirk_teal.png'),
 (565L, 35L, u'Teal', u'faceparts/lips_teal.png'),
 (566L, 36L, u'Black', u'faceparts/nose_black.png'),
 (567L, 36L, u'Brown', u'faceparts/nose_brown.png'),
 (568L, 36L, u'Brown Dark', u'faceparts/nose_brown_dark.png'),
 (569L, 36L, u'Cream', u'faceparts/nose_cream.png'),
 (570L, 36L, u'Creampng', u'faceparts/nose_creampng.png'),
 (571L, 36L, u'Fair', u'faceparts/nose_fair.png'),
 (572L, 36L, u'Olive', u'faceparts/nose_olive.png'),
 (573L, 37L, u'Beannie', u'faceparts/accessories_hat_beannie.png'),
 (574L, 37L, u'Cap Black', u'faceparts/accessories_hat_cap_black.png'),
 (575L, 37L, u'Cap Blue', u'faceparts/accessories_hat_cap_blue.png'),
 (576L, 37L, u'Cap Brown', u'faceparts/accessories_hat_cap_brown.png'),
 (577L, 37L, u'Cap Gray', u'faceparts/accessories_hat_cap_gray.png'),
 (578L, 37L, u'Cap Green', u'faceparts/accessories_hat_cap_green.png'),
 (579L, 37L, u'Cap Pink', u'faceparts/accessories_hat_cap_pink.png'),
 (580L, 37L, u'Cap Purple', u'faceparts/accessories_hat_cap_purple.png'),
 (581L, 37L, u'Cap Red', u'faceparts/accessories_hat_cap_red.png'),
 (582L, 37L, u'Cap Teal', u'faceparts/accessories_hat_cap_teal.png'),
 (583L, 43L, u'Safari', u'faceparts/accessories_hat_safari.png'),
 (584L, 38L, u'Brown Dark', u'faceparts/cheeks_brown_dark.png'),
 (585L, 38L, u'Brown Light', u'faceparts/cheeks_brown_light.png'),
 (586L, 38L, u'Cream', u'faceparts/cheeks_cream.png'),
 (587L, 38L, u'Fair', u'faceparts/cheeks_fair.png'),
 (588L, 38L, u'Olive', u'faceparts/cheeks_olive.png'),
 (589L, 38L, u'Pink', u'faceparts/cheeks_pink.png'),
 (590L, 39L, u'Black', u'faceparts/eyelashes_black.png'),
 (591L, 39L, u'Blonde', u'faceparts/eyelashes_blonde.png'),
 (592L, 39L, u'Blue', u'faceparts/eyelashes_blue.png'),
 (593L, 39L, u'Brown Dark', u'faceparts/eyelashes_brown_dark.png'),
 (594L, 39L, u'Brown Light', u'faceparts/eyelashes_brown_light.png'),
 (595L, 39L, u'Green', u'faceparts/eyelashes_green.png'),
 (596L, 39L, u'Orange', u'faceparts/eyelashes_orange.png'),
 (597L, 39L, u'Pink', u'faceparts/eyelashes_pink.png'),
 (598L, 39L, u'Red', u'faceparts/eyelashes_red.png'),
 (599L, 39L, u'Teal', u'faceparts/eyelashes_teal.png'),
 (600L, 41L, u'Mazz Black', u'faceparts/glasses_mazz_black.png'),
 (601L, 41L, u'Mazz Blue', u'faceparts/glasses_mazz_blue.png'),
 (602L, 41L, u'Mazz Brown Dark', u'faceparts/glasses_mazz_brown_dark.png'),
 (603L, 41L, u'Mazz Green', u'faceparts/glasses_mazz_green.png'),
 (604L, 41L, u'Mazz Orange', u'faceparts/glasses_mazz_orange.png'),
 (605L, 41L, u'Mazz Pink', u'faceparts/glasses_mazz_pink.png'),
 (606L, 41L, u'Mazz Red', u'faceparts/glasses_mazz_red.png'),
 (607L, 41L, u'Mazz Teal', u'faceparts/glasses_mazz_teal.png'),
 (608L, 41L, u'Natalie Black', u'faceparts/glasses_natalie_black.png'),
 (609L, 42L, u'Black', u'faceparts/facial_beard_black.png'),
 (610L, 42L, u'Blonde', u'faceparts/facial_beard_blonde.png'),
 (611L, 42L, u'Blue', u'faceparts/facial_beard_blue.png'),
 (612L, 42L, u'Brown', u'faceparts/facial_beard_brown.png'),
 (613L, 42L, u'Brown Dark', u'faceparts/facial_beard_brown_dark.png'),
 (614L, 42L, u'Brown Light', u'faceparts/facial_beard_brown_light.png'),
 (615L, 42L, u'Gray', u'faceparts/facial_beard_gray.png'),
 (616L, 42L, u'Gray Dark', u'faceparts/facial_beard_gray_dark.png'),
 (617L, 42L, u'Green', u'faceparts/facial_beard_green.png'),
 (618L, 42L, u'Orange', u'faceparts/facial_beard_orange.png'),
 (619L, 42L, u'Pink', u'faceparts/facial_beard_pink.png'),
 (620L, 42L, u'Purple', u'faceparts/facial_beard_purple.png'),
 (621L, 42L, u'Red', u'faceparts/facial_beard_red.png'),
 (622L, 42L, u'White', u'faceparts/facial_beard_white.png'),
 (623L, 40L, u'Beige', u'faceparts/face_beige.png'),
 (624L, 40L, u'Dark Brown', u'faceparts/face_brown_dark.png'),
 (625L, 40L, u'Light Brown', u'faceparts/face_brown_light.png'),
 (626L, 40L, u'Brown', u'faceparts/face_brown.png'),
 (627L, 40L, u'Cream', u'faceparts/face_cream.png'),
 (628L, 40L, u'Olive', u'faceparts/face_olive.png'),
 (629L, 40L, u'Fair', u'faceparts/face_fair.png')),
    delete_ids = [470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629]
)
