<xsl:stylesheet version="2.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:html="http://www.w3.org/1999/xhtml" exclude-result-prefixes="html">
  <xsl:output method="text"/>
  <xsl:template match="/">
    <xsl:for-each select="//html:td[html:a and contains(lower-case(.),'update')]">
      <xsl:value-of select="html:a/@href"/>|<xsl:value-of select="substring-after(../html:td[html:object]/@class,' ')"/><xsl:text>&#x0A;</xsl:text>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet> 