﻿package com.supereveildevfort.nov2008.profilepicture.ui.buttons {	import com.supereveildevfort.nov2008.profilepicture.ui.ArialText;		import com.supereveildevfort.nov2008.profilepicture.ui.RockwellText;			import flash.display.Sprite;			import com.niquimerret.accessibility.components.AccessButton;	import flash.text.TextFormat; 	/**	 * @class SubTabButton.as	 * @namespace com.supereveildevfort.nov2008.profilepicture.ui.buttons	 * @author Niqui Merret	 * @version 1.0	 * @date Nov 24, 2008	 * @description	 * @usage	 * NOTE:	 * TODO:	 *	 */	public class SubTabButton extends AccessButton 	{		private var mActive : Boolean = true;		private var mDisplayLable : ArialText;		private var mActiveFormat : TextFormat;		private var mInActiveFormat : TextFormat;		private var mBG : Sprite;		public function SubTabButton (pLabel : String, pDescription : String = "")		{						super(pLabel, pDescription);						}				/**		*********************************************************************************************************************************************************		* getter and setters		*********************************************************************************************************************************************************		*/				public function getLabel () : String		{			return mLabel;		}		public function get active() : Boolean		{			return mActive;		}				public function set active(pActive : Boolean) : void		{			mActive = pActive;			if (mActive) 			{				mDisplayLable.textFormat = mActiveFormat;			}			else			{				mDisplayLable.textFormat = mInActiveFormat;			}						mDisplayLable.autoWidth = true;		}						override protected function init() : void		{						super.init();						/*			mBG = new Sprite();			addChild(mBG);			mBG.graphics.beginFill(0x000000, 0.1);			mBG.graphics.drawRect(0, 0, 90, 15);			mBG.graphics.endFill();						 * 			 */			 			mInActiveFormat = new TextFormat(null, 12, 0x2E3192);			mActiveFormat = new TextFormat(null, 12, 0x42210B);						mDisplayLable = new ArialText(mLabel);			addChild(mDisplayLable);						mDisplayLable.textFormat = mActiveFormat;			mDisplayLable.autoWidth = true;		}				override protected function clickedAction() : void 		{			active = !mActive;		}			}}