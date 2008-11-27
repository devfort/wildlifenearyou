﻿package com.supereveildevfort.nov2008.profilepicture.ui.buttons {	import flash.display.Sprite;		import flash.display.Bitmap;			import com.niquimerret.accessibility.components.AccessButton; 		/**	 * @class Elements.as	 * @namespace com.supereveildevfort.nov2008.profilepicture.ui	 * @author Niqui Merret	 * @version 1.0	 * @date Nov 24, 2008	 * @description	 * @usage	 * NOTE:	 * TODO:	 *	 */	public class ElementButton extends AccessButton 	{		private var mBG : Sprite;		private var mBGOver : Sprite;		private var mBGSelected : Sprite;		public function ElementButton(pLable : String) 		{			super(pLable);		}						public function setUp(pDisplay : Bitmap) : void		{						mBGSelected = new Sprite();			mBGSelected.graphics.beginFill(0xcbe3ed, 0.5);			mBGSelected.graphics.drawRect(0, 0, pDisplay.width, pDisplay.height);			mBGSelected.graphics.endFill();			mBGSelected.visible = false;			addChild(mBGSelected);						mBG = new Sprite();			mBG.graphics.lineStyle(1, 0x2356d6, 0.2);			mBG.graphics.drawRect(0, 0, pDisplay.width, pDisplay.height);			mBG.graphics.endFill();			addChild(mBG);			//#CBE3ED			//ed8e7ef			mBGOver = new Sprite();			mBGOver.graphics.lineStyle(3, 0x2356d6, 0.5);			mBGOver.graphics.drawRect(0, 0, pDisplay.width, pDisplay.height);			mBGOver.graphics.endFill();			mBGOver.visible = false;			addChild(mBGOver);						addChild(pDisplay);								}							public function set selected (pSelected : Boolean) : void		{			mBGSelected.visible = pSelected;		}				override protected function focusInAction () : void		{						mBG.visible = false;			mBGOver.visible = true;					}						override protected function focusOutAction () : void		{			mBG.visible = true;			mBGOver.visible = false;		}							}	}