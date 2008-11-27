﻿package com.supereveildevfort.nov2008.profilepicture.ui.buttons {	import com.supereveildevfort.nov2008.profilepicture.ui.RockwellText;			import flash.display.Sprite;			import com.niquimerret.accessibility.components.AccessButton;	import flash.utils.getDefinitionByName;	import flash.text.TextFormat; 	/**	 * @class TabButton.as	 * @namespace com.supereveildevfort.nov2008.profilepicture.ui.buttons	 * @author Niqui Merret	 * @version 1.0	 * @date Nov 24, 2008	 * @description	 * @usage	 * NOTE:	 * TODO:	 *	 */	public class TabButton extends AccessButton 	{		private var mTab : Sprite;		private var mTabSelected : Sprite;		private var mActive : Boolean = true;		private var mDisplayLable : RockwellText;		private var mActiveFormat : TextFormat;		private var mInActiveFormat : TextFormat;		public function TabButton (pLabel : String, pDescription : String = "")		{						super(pLabel, pDescription);						}				/**		*********************************************************************************************************************************************************		* getter and setters		*********************************************************************************************************************************************************		*/				public function get active() : Boolean		{			return mActive;		}				public function set active(pActive : Boolean) : void		{			mActive = pActive;			if (mActive) 			{				mTabSelected.visible = false;				mTab.visible = true;				mDisplayLable.textFormat = mActiveFormat;			}			else			{				mTabSelected.visible = true;				mTab.visible = false;				mDisplayLable.textFormat = mInActiveFormat;			}		}						override protected function init() : void		{						super.init();						mInActiveFormat = new TextFormat(null, null, 0xFFFFFF);			mActiveFormat = new TextFormat(null, null, 0x42210B);						mTab = new Sprite();			addChild(mTab);						mTabSelected = new Sprite();			addChild(mTabSelected);						var tabImgC : Class = getDefinitionByName("tab") as Class;			var tabImg : Sprite = new tabImgC() as Sprite; 			mTab.addChild(tabImg); 						var tabSelImgC : Class = getDefinitionByName("tabSelected") as Class;			var tabSel : Sprite = new tabSelImgC() as Sprite; 			mTabSelected.addChild(tabSel);						mDisplayLable = new RockwellText(mLabel);			addChild(mDisplayLable);						mDisplayLable.x = Math.round(mTab.width/2 - mDisplayLable.width/2);			mDisplayLable.y = Math.round(mTab.height/2 - mDisplayLable.height/2);						mDisplayLable.textFormat = mActiveFormat;			mTabSelected.visible = false;		}				override protected function clickedAction() : void 		{			active = !mActive;		}			}}