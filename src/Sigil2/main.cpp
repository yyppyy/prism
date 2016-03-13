#include "Sigil.hpp"
#include <iostream>

void prettyPrintSigil2()
{
	std::string title =
"                                                                 \n"
"     .M\"\"\"bgd `7MMF' .g8\"\"\"bgd `7MMF'`7MMF'                \n"
"     ,MI    \"Y   MM .dP'     `M   MM    MM                      \n"
"     `MMb.       MM dM'       `   MM    MM         pd*\"*b.      \n"
"       `YMMNq.   MM MM            MM    MM        (O)   j8       \n"
"     .     `MM   MM MM.    `7MMF' MM    MM      ,     ,;j9     \n"
"     Mb     dM   MM `Mb.     MM   MM    MM     ,M  ,-='        \n"
"     P\"Ybmmd\"  .JMML. `\"bmmmdPY .JMML..JMMmmmmMMM Ammmmmmm  \n"
"                                                               \n"
"                                                               \n";
	std::cerr << title;
}

int main(int argc, char* argv[])
{
	prettyPrintSigil2();

	Sigil::instance().parseOptions(argc, argv);
	Sigil::instance().generateEvents();
}
