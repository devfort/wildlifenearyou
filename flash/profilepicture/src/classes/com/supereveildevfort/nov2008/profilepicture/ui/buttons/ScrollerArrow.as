﻿package com.supereveildevfort.nov2008.profilepicture.ui.buttons {	import flash.display.Sprite;		import flash.utils.getDefinitionByName;			import com.niquimerret.accessibility.components.AccessButton; 		/**	 * @class ScrollerArrow.as	 * @namespace com.supereveildevfort.nov2008.profilepicture.ui.buttons	 * @author Niqui Merret	 * @version 1.0	 * @date Nov 24, 2008	 * @description	 * @usage	 * NOTE:	 * TODO:	 *	 */	public class ScrollerArrow extends AccessButton 	{		private var mArrow : Sprite;		private var mArrowOver : Sprite;		public function ScrollerArrow(pLable : String)		{						super(pLable);						}						override protected function init () : void		{			super.init();			mArrow = new Sprite();			addChild(mArrow);						mArrowOver = new Sprite();			addChild(mArrowOver);				var arrowC : Class = getDefinitionByName("Arrow") as Class;			var arrowImg : Sprite = new arrowC() as Sprite;			mArrow.addChild(arrowImg);						var arrowOver : Sprite = new Sprite();			addChild(arrowOver);				var arrowOverC : Class = getDefinitionByName("ArrowOver") as Class;			var arrowOverImg : Sprite = new arrowOverC() as Sprite;			mArrowOver.addChild(arrowOverImg);			mArrowOver.visible = false;							}						override protected function focusInAction () : void		{						mArrow.visible = false;			mArrowOver.visible = true;					}						override protected function focusOutAction () : void		{			mArrow.visible = true;			mArrowOver.visible = false;		}					}}