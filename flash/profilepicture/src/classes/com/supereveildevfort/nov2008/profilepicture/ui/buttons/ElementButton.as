﻿package com.supereveildevfort.nov2008.profilepicture.ui.buttons {	import flash.display.Bitmap;			import com.niquimerret.accessibility.components.AccessButton; 		/**	 * @class Elements.as	 * @namespace com.supereveildevfort.nov2008.profilepicture.ui	 * @author Niqui Merret	 * @version 1.0	 * @date Nov 24, 2008	 * @description	 * @usage	 * NOTE:	 * TODO:	 *	 */	public class ElementButton extends AccessButton 	{				public function ElementButton(pLable : String) 		{			super(pLable);		}						public function setUp(pDisplay : Bitmap) : void		{			addChild(pDisplay);		}			}	}