﻿package com.supereveildevfort.nov2008.profilepicture.controllers {	import com.supereveildevfort.nov2008.profilepicture.ui.TabSubMenu;		import com.supereveildevfort.nov2008.profilepicture.ui.ElementsScroller;		import com.supereveildevfort.nov2008.profilepicture.controllers.ElementsPanelController;		import com.supereveildevfort.nov2008.profilepicture.events.SubTabEvent;		import com.supereveildevfort.nov2008.profilepicture.model.ProfileImages;		import com.niquimerret.events.InteractionEvent;		import com.supereveildevfort.nov2008.profilepicture.ui.buttons.TabButton;			import flash.display.Sprite;import flash.utils.getDefinitionByName; 		/**	 * @class TabWindow.as	 * @namespace com.supereveildevfort.nov2008.profilepicture.ui	 * @author Niqui Merret	 * @version 1.0	 * @date Nov 25, 2008	 * @description	 * @usage	 * NOTE:	 * TODO:	 *	 */	public class TabWindowController extends Sprite 	{		private var mTabBG : Sprite;		private var mProfileImages : ProfileImages;		private var mTabList : Array;		private var mSubMenu : TabSubMenu;		private var mActiveTabID : Number = 0;		private var mElementsScroller : ElementsScroller;		private var mElementsPanelController : ElementsPanelController;		public function TabWindowController (pProfileImages : ProfileImages)		{			mProfileImages = pProfileImages;			init();		}				private function onTabClicked (e : InteractionEvent) : void		{									var i : uint;			var len : uint = mProfileImages.faceareacategories.length;						for (i = 0; i < len; i++) 			{							if (e.currentTarget != mTabList[i])				{					mTabList[i].active = false;				}				else				{					mActiveTabID = i;					mTabList[i].active = true;				}			}			mSubMenu.setMenuItems(mProfileImages.faceareacategories[mActiveTabID].faceareas);					}				private function init() : void		{						mTabBG = new Sprite();			addChild(mTabBG);						var tabBGC : Class = getDefinitionByName("tabbg") as Class;			var tabBG : Sprite =  new tabBGC() as Sprite;			mTabBG.addChild(tabBG);						var i : uint;			var len : uint = mProfileImages.faceareacategories.length;			var tab : TabButton;			mTabList = new Array();						for (i = 0; i < len; i++) 			{								tab = new TabButton(mProfileImages.faceareacategories[i].name);				addChild(tab);				tab.addEventListener(InteractionEvent.CLICKED, onTabClicked);				tab.x = 15 + (tab.width+5)*i;				tab.active = false;				mTabList.push(tab);							}						mTabList[mActiveTabID].active = true;			mTabBG.y = mTabList[mActiveTabID].height - 3;						mSubMenu = new TabSubMenu();			addChild(mSubMenu);			mSubMenu.y = mTabList[mActiveTabID].height + 5;			mSubMenu.setMenuItems(mProfileImages.faceareacategories[mActiveTabID].faceareas);			mSubMenu.addEventListener(SubTabEvent.SUB_TAB_SELECTED, onSubTabSelected);						mElementsScroller = new ElementsScroller();			addChild(mElementsScroller);			mElementsScroller.y = mSubMenu.y + mSubMenu.height + 10;			mElementsScroller.x = 20;						mElementsPanelController = new ElementsPanelController();			addChild(mElementsPanelController);			mElementsPanelController.y = mSubMenu.y + mSubMenu.height + 10;			mElementsPanelController.x = 10;			mElementsPanelController.setUp(mProfileImages);						mElementsScroller.elementsPanel = mElementsPanelController.activatePanel(mSubMenu.selected);		}						private function onSubTabSelected (e : SubTabEvent) : void		{						mElementsScroller.elementsPanel = mElementsPanelController.activatePanel(e.lable);					}	}}